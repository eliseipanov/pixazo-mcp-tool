#!/usr/bin/env python3
"""
Seed script to add default request/response templates for SDXL and Flux Klein models.
Run this after migration to populate the templates.
"""

import os
import sys
import json

# Change to ai-workspace-app directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

from app import app, db, GenerativeModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Default templates for SDXL
SDXL_REQUEST_TEMPLATE = json.dumps({
    "endpoint": "/v1/generate/sdxl",
    "include_params": ["prompt", "width", "height", "num_steps", "guidance_scale", "seed"],
    "exclude_params": [],
    "param_mapping": {}
})

SDXL_RESPONSE_TEMPLATE = json.dumps({
    "image_url_path": "imageUrl",
    "success_path": "status",
    "error_path": "error"
})


# Default templates for Flux Klein
FLUX_REQUEST_TEMPLATE = json.dumps({
    "endpoint": "/v1/generate/flux",
    "include_params": ["prompt", "width", "height", "num_steps", "seed"],
    "exclude_params": ["guidance_scale"],
    "param_mapping": {
        "num_steps": "num_inference_steps"
    }
})

FLUX_RESPONSE_TEMPLATE = json.dumps({
    "image_url_path": "output",
    "success_path": "status",
    "error_path": "error"
})


def seed_templates():
    """Add default templates to models."""
    with app.app_context():
        try:
            # Update SDXL model
            sdxl_model = GenerativeModel.query.filter_by(name='sdxl').first()
            if sdxl_model:
                sdxl_model.request_template = SDXL_REQUEST_TEMPLATE
                sdxl_model.response_template = SDXL_RESPONSE_TEMPLATE
                logger.info(f"Updated templates for SDXL model: {sdxl_model.display_name}")
            else:
                logger.warning("SDXL model not found in database")
            
            # Update Flux Klein model
            flux_model = GenerativeModel.query.filter_by(name='flux').first()
            if flux_model:
                flux_model.request_template = FLUX_REQUEST_TEMPLATE
                flux_model.response_template = FLUX_RESPONSE_TEMPLATE
                logger.info(f"Updated templates for Flux Klein model: {flux_model.display_name}")
            else:
                logger.warning("Flux Klein model not found in database")
            
            db.session.commit()
            logger.info("Templates seeded successfully!")
            
        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            db.session.rollback()
            raise


if __name__ == '__main__':
    seed_templates()
