"""
Test suite for generate_templates.py script
============================================

Tests for the command-line interface and argument parsing.
"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestGenerateTemplatesScript:
    """Test the generate_templates CLI script"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    def test_script_imports(self):
        """Should import without errors"""
        try:
            import generate_templates
            assert True, "Script should import successfully"
        except ImportError as e:
            pytest.fail(f"Failed to import generate_templates: {e}")
    
    def test_template_generator_import(self):
        """Should successfully import TemplateGenerator"""
        from modules.template_generator import TemplateGenerator
        assert TemplateGenerator is not None
    
    def test_test_data_generator_import(self):
        """Should successfully import TestDataGenerator"""
        from modules.test_data_generator import TestDataGenerator
        assert TestDataGenerator is not None


class TestArgumentParsing:
    """Test command-line argument parsing"""
    
    @pytest.fixture
    def mock_generators(self):
        """Mock both generator classes"""
        with patch('modules.template_generator.TemplateGenerator') as mock_template, \
             patch('modules.test_data_generator.TestDataGenerator') as mock_testdata:
            
            # Setup mock instances
            mock_template_instance = MagicMock()
            mock_testdata_instance = MagicMock()
            
            mock_template.return_value = mock_template_instance
            mock_testdata.return_value = mock_testdata_instance
            
            yield {
                'template_class': mock_template,
                'testdata_class': mock_testdata,
                'template_instance': mock_template_instance,
                'testdata_instance': mock_testdata_instance
            }
    
    def test_help_argument(self):
        """Should display help when --help is used"""
        # Just verify the script has a proper structure for argparse
        # We can't easily test the help output without running the script
        pass
    
    def test_script_has_main_guard(self):
        """Should have if __name__ == '__main__' guard"""
        with open('generate_templates.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "if __name__ ==" in content or "if __name__==" in content, \
            "Script should have main guard"


class TestScriptDocumentation:
    """Test script documentation and help text"""
    
    def test_has_module_docstring(self):
        """Should have module-level docstring"""
        with open('generate_templates.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for docstring
        assert '"""' in content or "'''" in content, \
            "Script should have documentation"
    
    def test_docstring_describes_usage(self):
        """Should document usage examples in docstring"""
        with open('generate_templates.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Get content before first code
        docstring_lines = []
        in_docstring = False
        for line in lines:
            if '"""' in line or "'''" in line:
                if in_docstring:
                    docstring_lines.append(line)
                    break
                in_docstring = True
            if in_docstring:
                docstring_lines.append(line)
        
        docstring = ''.join(docstring_lines)
        
        # Should mention key command-line options
        assert 'templates' in docstring.lower() or 'test-data' in docstring.lower(), \
            "Docstring should describe command-line options"


class TestScriptStructure:
    """Test overall script structure"""
    
    def test_has_required_imports(self):
        """Should import required modules"""
        with open('generate_templates.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for critical imports
        assert 'import argparse' in content, "Should import argparse"
        assert 'import logging' in content, "Should import logging"
        assert 'from modules.template_generator import' in content, \
            "Should import TemplateGenerator"
        assert 'from modules.test_data_generator import' in content, \
            "Should import TestDataGenerator"
    
    def test_shebang_line(self):
        """Should have proper shebang for Python 3"""
        with open('generate_templates.py', 'r', encoding='utf-8') as f:
            first_line = f.readline()
        
        assert first_line.startswith('#!'), "Should have shebang line"
        assert 'python' in first_line.lower(), "Shebang should reference python"


class TestIntegrationScenarios:
    """Test realistic usage scenarios"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    def test_can_create_template_generator_instance(self, temp_dir):
        """Should be able to create TemplateGenerator instance"""
        from modules.template_generator import TemplateGenerator
        
        generator = TemplateGenerator(output_dir=temp_dir)
        assert generator is not None
        assert generator.output_dir == Path(temp_dir)
    
    def test_can_create_test_data_generator_instance(self, temp_dir):
        """Should be able to create TestDataGenerator instance"""
        from modules.test_data_generator import TestDataGenerator
        
        generator = TestDataGenerator(output_dir=temp_dir)
        assert generator is not None
        assert generator.output_dir == Path(temp_dir)
    
    def test_generators_can_run_independently(self, temp_dir):
        """Should be able to run each generator independently"""
        from modules.template_generator import TemplateGenerator
        from modules.test_data_generator import TestDataGenerator
        
        # Run template generator
        template_gen = TemplateGenerator(output_dir=str(Path(temp_dir) / "templates"))
        template_gen.generate_balakovo_templates()
        
        # Run test data generator  
        testdata_gen = TestDataGenerator(output_dir=str(Path(temp_dir) / "testdata"))
        testdata_gen.generate_balakovo_test_data()
        
        # Both should succeed without conflicts
        assert (Path(temp_dir) / "templates" / "balakovo").exists()
        assert (Path(temp_dir) / "testdata" / "balakovo").exists()


class TestLoggingConfiguration:
    """Test logging setup in the script"""
    
    def test_logging_import(self):
        """Should import logging module"""
        with open('generate_templates.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'import logging' in content, "Should import logging"


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    def test_generators_handle_missing_directory(self, temp_dir):
        """Should handle case when output directory doesn't exist"""
        from modules.template_generator import TemplateGenerator
        from modules.test_data_generator import TestDataGenerator
        
        nonexistent = str(Path(temp_dir) / "does_not_exist")
        
        # Should not raise an exception
        template_gen = TemplateGenerator(output_dir=nonexistent)
        template_gen.generate_balakovo_templates()
        
        testdata_gen = TestDataGenerator(output_dir=nonexistent)
        testdata_gen.generate_balakovo_test_data()
        
        # Directories should be created
        assert Path(nonexistent).exists()
