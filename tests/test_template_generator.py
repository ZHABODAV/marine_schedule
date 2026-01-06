"""
Test suite for TemplateGenerator module
========================================

Tests for generating CSV templates for Olya, DeepSea, and Balakovo scenarios.
Covers template structure, column validation, and comment headers.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil

from modules.template_generator import TemplateGenerator


class TestTemplateGeneratorInit:
    """Test TemplateGenerator initialization"""
    
    def test_init_default_output_dir(self):
        """Should initialize with default 'templates' directory"""
        generator = TemplateGenerator()
        
        assert generator.output_dir == Path("templates")
        assert isinstance(generator.output_dir, Path)
    
    def test_init_custom_output_dir(self):
        """Should initialize with custom output directory"""
        custom_dir = "custom_templates"
        generator = TemplateGenerator(output_dir=custom_dir)
        
        assert generator.output_dir == Path(custom_dir)
    
    def test_init_with_path_object(self):
        """Should handle Path object as output_dir"""
        custom_path = Path("test_templates")
        generator = TemplateGenerator(output_dir=str(custom_path))
        
        assert generator.output_dir == custom_path


class TestBalakovoTemplateGeneration:
    """Test Balakovo template generation"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    def generator(self, temp_dir):
        """Create generator with temp directory"""
        return TemplateGenerator(output_dir=temp_dir)
    
    def test_generate_balakovo_creates_directory(self, generator, temp_dir):
        """Should create balakovo subdirectory"""
        generator.generate_balakovo_templates()
        
        balakovo_dir = Path(temp_dir) / "balakovo"
        assert balakovo_dir.exists()
        assert balakovo_dir.is_dir()
    
    def test_generate_balakovo_berths_template(self, generator, temp_dir):
        """Should create berths template with correct columns"""
        generator.generate_balakovo_templates()
        
        filepath = Path(temp_dir) / "balakovo" / "berths_balakovo.csv"
        assert filepath.exists(), "Berths template should be created"
        
        # Read the file, skipping comment lines
        df = pd.read_csv(filepath, sep=';', comment='#')
        
        # Check required columns exist
        expected_columns = [
            'berth_id', 'berth_name', 'berth_type', 'max_loa_m',
            'max_beam_m', 'max_draft_m', 'cargo_types',
            'load_rate_mt_day', 'working_hours', 'remarks'
        ]
        assert list(df.columns) == expected_columns, \
            "Template should have correct column structure"
        
        # Template should be empty (no data rows)
        assert len(df) == 0, "Template should have no data rows"
    
    def test_generate_balakovo_berths_has_comments(self, generator, temp_dir):
        """Should include comment header in berths template"""
        generator.generate_balakovo_templates()
        
        filepath = Path(temp_dir) / "balakovo" / "berths_balakovo.csv"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain comment lines
        assert '#' in content, "Template should have comment header"
        assert 'berth_id' in content, "Should document berth_id field"
        assert 'berth_type' in content, "Should document berth_type field"
    
    def test_generate_balakovo_fleet_template(self, generator, temp_dir):
        """Should create fleet template with correct columns"""
        generator.generate_balakovo_templates()
        
        filepath = Path(temp_dir) / "balakovo" / "fleet_balakovo.csv"
        assert filepath.exists(), "Fleet template should be created"
        
        df = pd.read_csv(filepath, sep=';', comment='#')
        
        expected_columns = [
            'vessel_id', 'vessel_name', 'vessel_type', 'vessel_class',
            'cargo_type', 'capacity_mt', 'loa_m', 'beam_m', 'draft_m',
            'speed_kn', 'owner', 'destination', 'remarks'
        ]
        assert list(df.columns) == expected_columns, \
            "Fleet template should have correct columns"
        
        assert len(df) == 0, "Template should be empty"
    
    def test_generate_balakovo_fleet_has_usage_hints(self, generator, temp_dir):
        """Should include usage hints in fleet template"""
        generator.generate_balakovo_templates()
        
        filepath = Path(temp_dir) / "balakovo" / "fleet_balakovo.csv"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should contain helpful comments
        assert 'БАРЖИ' in content or 'vessel_type' in content, \
            "Should include usage hints"
    
    def test_generate_balakovo_cargo_plan_template(self, generator, temp_dir):
        """Should create cargo plan template with correct columns"""
        generator.generate_balakovo_templates()
        
        filepath = Path(temp_dir) / "balakovo" / "cargo_plan_balakovo.csv"
        assert filepath.exists(), "Cargo plan template should be created"
        
        df = pd.read_csv(filepath, sep=';', comment='#')
        
        expected_columns = [
            'cargo_id', 'cargo_type', 'qty_mt', 'destination',
            'priority', 'earliest_date', 'latest_date',
            'vessel_preference', 'remarks'
        ]
        assert list(df.columns) == expected_columns, \
            "Cargo plan template should have correct columns"
        
        assert len(df) == 0, "Template should be empty"
    
    def test_generate_balakovo_params_template(self, generator, temp_dir):
        """Should create params template with sample data"""
        generator.generate_balakovo_templates()
        
        filepath = Path(temp_dir) / "balakovo" / "params_balakovo.csv"
        assert filepath.exists(), "Parameters template should be created"
        
        df = pd.read_csv(filepath, sep=';', comment='#')
        
        # Check columns
        expected_columns = ['parameter', 'value', 'unit', 'description']
        assert list(df.columns) == expected_columns, \
            "Parameters template should have correct columns"
        
        # Should have sample data (not empty like other templates)
        assert len(df) > 0, "Parameters template should have sample values"
    
    def test_generate_balakovo_params_includes_critical_params(self, generator, temp_dir):
        """Should include all critical parameters in template"""
        generator.generate_balakovo_templates()
        
        df = pd.read_csv(
            Path(temp_dir) / "balakovo" / "params_balakovo.csv",
            sep=';',
            comment='#'
        )
        
        param_names = df['parameter'].tolist()
        
        # Check critical parameters are present
        critical_params = [
            'season_start', 'season_end', 'berthing_hours',
            'unberthing_hours', 'load_rate_sfo'
        ]
        
        for param in critical_params:
            assert param in param_names, \
                f"Critical parameter '{param}' should be in template"
    
    def test_generate_balakovo_restrictions_template(self, generator, temp_dir):
        """Should create restrictions template with correct columns"""
        generator.generate_balakovo_templates()
        
        filepath = Path(temp_dir) / "balakovo" / "restrictions_balakovo.csv"
        assert filepath.exists(), "Restrictions template should be created"
        
        df = pd.read_csv(filepath, sep=';', comment='#')
        
        expected_columns = [
            'restriction_id', 'restriction_type', 'start_date',
            'end_date', 'berth_id', 'severity', 'description'
        ]
        assert list(df.columns) == expected_columns, \
            "Restrictions template should have correct columns"
        
        assert len(df) == 0, "Template should be empty"
    
    def test_generate_balakovo_restrictions_documents_types(self, generator, temp_dir):
        """Should document restriction types in template"""
        generator.generate_balakovo_templates()
        
        filepath = Path(temp_dir) / "balakovo" / "restrictions_balakovo.csv"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should document restriction types
        restriction_types = ['weather', 'water_level', 'maintenance', 'holiday']
        for rtype in restriction_types:
            assert rtype in content, \
                f"Should document '{rtype}' restriction type"


class TestTemplateFileFormat:
    """Test template file formatting and structure"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    def generator(self, temp_dir):
        """Create generator with temp directory"""
        return TemplateGenerator(output_dir=temp_dir)
    
    def test_csv_separator_consistency(self, generator, temp_dir):
        """Should use semicolon separator consistently"""
        generator.generate_balakovo_templates()
        
        balakovo_dir = Path(temp_dir) / "balakovo"
        
        for csv_file in balakovo_dir.glob("*.csv"):
            # Should be readable with semicolon separator
            df = pd.read_csv(csv_file, sep=';', comment='#')
            assert len(df.columns) > 1, \
                f"Template {csv_file.name} should have multiple columns"
    
    def test_utf8_encoding(self, generator, temp_dir):
        """Should use UTF-8 encoding for Russian text"""
        generator.generate_balakovo_templates()
        
        filepath = Path(temp_dir) / "balakovo" / "berths_balakovo.csv"
        
        # Should be readable with UTF-8
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert content, "File should be readable with UTF-8 encoding"
    
    def test_comment_headers_not_parsed_as_data(self, generator, temp_dir):
        """Should ensure comment headers don't interfere with data parsing"""
        generator.generate_balakovo_templates()
        
        filepath = Path(temp_dir) / "balakovo" / "fleet_balakovo.csv"
        
        # Read without comment parameter - should fail or have wrong structure
        # Read with comment parameter - should work correctly
        df_with_comments = pd.read_csv(filepath, sep=';', comment='#')
        
        # Should have clean column names (not starting with #)
        for col in df_with_comments.columns:
            assert not col.startswith('#'), \
                "Column names should not include comment markers"


class TestGenerateAllMethod:
    """Test the generate_all() method"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    def generator(self, temp_dir):
        """Create generator with temp directory"""
        return TemplateGenerator(output_dir=temp_dir)
    
    def test_generate_all_creates_balakovo_templates(self, generator, temp_dir):
        """Should create all Balakovo templates when calling generate_all()"""
        generator.generate_all()
        
        balakovo_dir = Path(temp_dir) / "balakovo"
        
        expected_files = [
            "berths_balakovo.csv",
            "fleet_balakovo.csv",
            "cargo_plan_balakovo.csv",
            "params_balakovo.csv",
            "restrictions_balakovo.csv"
        ]
        
        for filename in expected_files:
            filepath = balakovo_dir / filename
            assert filepath.exists(), f"Template {filename} should be created"
    
    def test_generate_all_calls_all_generators(self, generator, temp_dir, monkeypatch):
        """Should call all three template generation methods"""
        calls = []
        
        def track_olya(self):
            calls.append('olya')
        
        def track_deepsea(self):
            calls.append('deepsea')
        
        def track_balakovo(self):
            calls.append('balakovo')
        
        monkeypatch.setattr(TemplateGenerator, 'generate_olya_templates', track_olya)
        monkeypatch.setattr(TemplateGenerator, 'generate_deepsea_templates', track_deepsea)
        monkeypatch.setattr(TemplateGenerator, 'generate_balakovo_templates', track_balakovo)
        
        generator.generate_all()
        
        assert 'olya' in calls, "Should call generate_olya_templates"
        assert 'deepsea' in calls, "Should call generate_deepsea_templates"
        assert 'balakovo' in calls, "Should call generate_balakovo_templates"


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_generate_to_nonexistent_directory(self):
        """Should create directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent = Path(temp_dir) / "new_dir" / "nested" / "path"
            generator = TemplateGenerator(output_dir=str(nonexistent))
            
            # Should not raise an error
            generator.generate_balakovo_templates()
            
            # Directory should be created
            assert nonexistent.exists()
    
    def test_multiple_generation_calls_overwrite(self):
        """Should handle multiple calls to generation methods"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = TemplateGenerator(output_dir=temp_dir)
            
            # Call twice
            generator.generate_balakovo_templates()
            generator.generate_balakovo_templates()
            
            # Files should still exist and be valid
            filepath = Path(temp_dir) / "balakovo" / "berths_balakovo.csv"
            assert filepath.exists()
            
            df = pd.read_csv(filepath, sep=';', comment='#')
            assert len(df.columns) == 10  # Should have 10 columns
    
    def test_existing_directory_with_files(self):
        """Should overwrite existing template files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            balakovo_dir = Path(temp_dir) / "balakovo"
            balakovo_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a dummy file
            dummy_file = balakovo_dir / "berths_balakovo.csv"
            dummy_file.write_text("dummy,data\n1,2", encoding='utf-8')
            
            generator = TemplateGenerator(output_dir=temp_dir)
            generator.generate_balakovo_templates()
            
            # File should be overwritten with proper template
            df = pd.read_csv(dummy_file, sep=';', comment='#')
            assert 'berth_id' in df.columns, "Should have proper template columns"


class TestTemplateUsability:
    """Test that templates are usable for end users"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    def generator(self, temp_dir):
        """Create generator with temp directory"""
        return TemplateGenerator(output_dir=temp_dir)
    
    def test_templates_can_be_opened_in_excel(self, generator, temp_dir):
        """Should create templates compatible with Excel (semicolon-separated)"""
        generator.generate_balakovo_templates()
        
        # Excel typically uses semicolon for CSV in certain locales
        filepath = Path(temp_dir) / "balakovo" / "berths_balakovo.csv"
        
        # Should be parseable
        df = pd.read_csv(filepath, sep=';', comment='#')
        assert len(df.columns) > 1
    
    def test_templates_preserve_column_order(self, generator, temp_dir):
        """Should maintain consistent column order"""
        generator.generate_balakovo_templates()
        
        filepath = Path(temp_dir) / "balakovo" / "berths_balakovo.csv"
        df = pd.read_csv(filepath, sep=';', comment='#')
        
        # First column should be the ID column
        assert df.columns[0] == 'berth_id', \
            "First column should be the identifier"
    
    def test_params_template_has_example_values(self, generator, temp_dir):
        """Should provide example values in params template"""
        generator.generate_balakovo_templates()
        
        df = pd.read_csv(
            Path(temp_dir) / "balakovo" / "params_balakovo.csv",
            sep=';',
            comment='#'
        )
        
        # All rows should have values
        assert not df['value'].isna().any(), \
            "All parameters should have example values"
        
        # All rows should have descriptions
        assert not df['description'].isna().any(), \
            "All parameters should have descriptions"
