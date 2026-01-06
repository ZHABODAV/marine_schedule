#!/usr/bin/env python3
"""
Template and Test Data Generation CLI
======================================

Command-line interface for generating CSV templates and test data for the
Maritime Voyage Planner project.

Usage Examples
--------------

Generate Balakovo templates:
    python generate_templates.py --templates --output-dir ./output/templates

Generate Balakovo test data:
    python generate_templates.py --test-data --output-dir ./output/testdata

Generate both templates and test data:
    python generate_templates.py --templates --test-data

Specify custom output directory:
    python generate_templates.py --templates --output-dir /path/to/output

Options
-------
--templates         Generate CSV templates with headers and comments
--test-data         Generate test data files with sample data
--output-dir PATH   Specify output directory (default: ./output)
--help, -h          Show this help message
"""

import argparse
import logging
import sys
from pathlib import Path

from modules.template_generator import TemplateGenerator
from modules.test_data_generator import TestDataGenerator


def setup_logging() -> None:
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main() -> int:
    """
    Main entry point for the template generation CLI.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description='Generate templates and test data for Maritime Voyage Planner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--templates',
        action='store_true',
        help='Generate CSV templates'
    )
    
    parser.add_argument(
        '--test-data',
        action='store_true',
        help='Generate test data files'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./output',
        help='Output directory for generated files (default: ./output)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Validate arguments
    if not args.templates and not args.test_data:
        logger.error("Please specify at least one option: --templates or --test-data")
        parser.print_help()
        return 1
    
    output_path = Path(args.output_dir)
    
    try:
        # Generate templates
        if args.templates:
            logger.info(f"Generating templates to: {output_path}")
            template_gen = TemplateGenerator(output_dir=str(output_path / 'templates'))
            template_gen.generate_all()
            logger.info("Templates generated successfully")
        
        # Generate test data
        if args.test_data:
            logger.info(f"Generating test data to: {output_path}")
            testdata_gen = TestDataGenerator(output_dir=str(output_path / 'testdata'))
            testdata_gen.generate_all()
            logger.info("Test data generated successfully")
        
        logger.info("All requested generations completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error during generation: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
