#!/usr/bin/env python3
"""
Cleanup script for old generated images.
This script can be used to:
1. Delete all generated images from the database and filesystem
2. Delete images older than a certain number of days
3. Delete images from a specific workspace
4. Delete orphaned files (files that exist but have no database record)
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Change to ai-workspace-app directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

from app import app, db, GeneratedImage, Workspace, User
from image_utils import get_thumbnail_path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def delete_image_record(image):
    """Delete a single image record and its files."""
    try:
        # Delete image file
        if image.path and os.path.exists(image.path):
            os.remove(image.path)
            logger.info(f"Deleted image file: {image.path}")
        
        # Delete thumbnail file
        if image.thumbnail_path and os.path.exists(image.thumbnail_path):
            os.remove(image.thumbnail_path)
            logger.info(f"Deleted thumbnail file: {image.thumbnail_path}")
        
        # Delete database record
        db.session.delete(image)
        logger.info(f"Deleted image record ID: {image.id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting image {image.id}: {e}")
        return False


def delete_all_images():
    """Delete all generated images."""
    with app.app_context():
        images = GeneratedImage.query.all()
        count = len(images)
        logger.info(f"Found {count} images to delete")
        
        deleted = 0
        for image in images:
            if delete_image_record(image):
                deleted += 1
        
        db.session.commit()
        logger.info(f"Deleted {deleted}/{count} images")


def delete_old_images(days):
    """Delete images older than specified days."""
    with app.app_context():
        cutoff_date = datetime.now() - timedelta(days=days)
        images = GeneratedImage.query.filter(GeneratedImage.created_at < cutoff_date).all()
        count = len(images)
        logger.info(f"Found {count} images older than {days} days")
        
        deleted = 0
        for image in images:
            if delete_image_record(image):
                deleted += 1
        
        db.session.commit()
        logger.info(f"Deleted {deleted}/{count} old images")


def delete_workspace_images(workspace_id):
    """Delete all images from a specific workspace."""
    with app.app_context():
        workspace = Workspace.query.get(workspace_id)
        if not workspace:
            logger.error(f"Workspace {workspace_id} not found")
            return
        
        images = GeneratedImage.query.filter_by(workspace_id=workspace_id).all()
        count = len(images)
        logger.info(f"Found {count} images in workspace '{workspace.name}'")
        
        deleted = 0
        for image in images:
            if delete_image_record(image):
                deleted += 1
        
        db.session.commit()
        logger.info(f"Deleted {deleted}/{count} images from workspace '{workspace.name}'")


def delete_orphaned_files():
    """Delete files that exist but have no database record."""
    with app.app_context():
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'generated')
        
        if not os.path.exists(data_dir):
            logger.info(f"Data directory does not exist: {data_dir}")
            return
        
        # Get all image paths from database
        db_paths = set()
        for image in GeneratedImage.query.all():
            if image.path:
                db_paths.add(image.path)
            if image.thumbnail_path:
                db_paths.add(image.thumbnail_path)
        
        # Find all files in data directory
        orphaned = []
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in db_paths:
                    orphaned.append(file_path)
        
        logger.info(f"Found {len(orphaned)} orphaned files")
        
        deleted = 0
        for file_path in orphaned:
            try:
                os.remove(file_path)
                logger.info(f"Deleted orphaned file: {file_path}")
                deleted += 1
            except Exception as e:
                logger.error(f"Error deleting orphaned file {file_path}: {e}")
        
        logger.info(f"Deleted {deleted}/{len(orphaned)} orphaned files")


def list_images():
    """List all images in the database."""
    with app.app_context():
        images = GeneratedImage.query.order_by(GeneratedImage.created_at.desc()).all()
        logger.info(f"Total images in database: {len(images)}")
        
        for image in images:
            workspace = Workspace.query.get(image.workspace_id)
            workspace_name = workspace.name if workspace else "Unknown"
            logger.info(
                f"ID: {image.id} | Workspace: {workspace_name} | "
                f"Created: {image.created_at} | Path: {image.path}"
            )


def main():
    parser = argparse.ArgumentParser(description='Cleanup script for generated images')
    parser.add_argument('--all', action='store_true', help='Delete all images')
    parser.add_argument('--old', type=int, metavar='DAYS', help='Delete images older than N days')
    parser.add_argument('--workspace', type=int, metavar='ID', help='Delete images from workspace ID')
    parser.add_argument('--orphaned', action='store_true', help='Delete orphaned files')
    parser.add_argument('--list', action='store_true', help='List all images')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    
    args = parser.parse_args()
    
    if args.list:
        list_images()
    elif args.all:
        if args.dry_run:
            logger.info("DRY RUN: Would delete all images")
            list_images()
        else:
            delete_all_images()
    elif args.old:
        if args.dry_run:
            logger.info(f"DRY RUN: Would delete images older than {args.old} days")
            # List images that would be deleted
            with app.app_context():
                cutoff_date = datetime.now() - timedelta(days=args.old)
                images = GeneratedImage.query.filter(GeneratedImage.created_at < cutoff_date).all()
                logger.info(f"Would delete {len(images)} images")
        else:
            delete_old_images(args.old)
    elif args.workspace:
        if args.dry_run:
            logger.info(f"DRY RUN: Would delete images from workspace {args.workspace}")
            # List images that would be deleted
            with app.app_context():
                workspace = Workspace.query.get(args.workspace)
                if workspace:
                    images = GeneratedImage.query.filter_by(workspace_id=args.workspace).all()
                    logger.info(f"Would delete {len(images)} images from workspace '{workspace.name}'")
        else:
            delete_workspace_images(args.workspace)
    elif args.orphaned:
        if args.dry_run:
            logger.info("DRY RUN: Would delete orphaned files")
            # List orphaned files
            with app.app_context():
                data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'generated')
                db_paths = set()
                for image in GeneratedImage.query.all():
                    if image.path:
                        db_paths.add(image.path)
                    if image.thumbnail_path:
                        db_paths.add(image.thumbnail_path)
                
                orphaned = []
                for root, dirs, files in os.walk(data_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file_path not in db_paths:
                            orphaned.append(file_path)
                
                logger.info(f"Would delete {len(orphaned)} orphaned files")
                for file_path in orphaned:
                    logger.info(f"  {file_path}")
        else:
            delete_orphaned_files()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
