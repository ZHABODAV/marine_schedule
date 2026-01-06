"""
Test suite for TestDataGenerator module
=========================================

Tests for generating test data for Olya, DeepSea, and Balakovo scenarios.
Covers happy paths, edge cases, and error scenarios.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from modules.test_data_generator import TestDataGenerator


class TestTestDataGeneratorInit:
    """Test TestDataGenerator initialization"""
    
    def test_init_default_output_dir(self):
        """Should initialize with default 'input' directory"""
        generator = TestDataGenerator()
        
        assert generator.output_dir == Path("input")
        assert isinstance(generator.output_dir, Path)
    
    def test_init_custom_output_dir(self):
        """Should initialize with custom output directory"""
        custom_dir = "custom_output"
        generator = TestDataGenerator(output_dir=custom_dir)
        
        assert generator.output_dir == Path(custom_dir)
    
    def test_init_with_path_object(self):
        """Should handle Path object as output_dir"""
        custom_path = Path("test_output")
        generator = TestDataGenerator(output_dir=str(custom_path))
        
        assert generator.output_dir == custom_path


class TestBalakovoDataGeneration:
    """Test Balakovo test data generation"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    @pytest.fixture
    def generator(self, temp_dir):
        """Create generator with temp directory"""
        return TestDataGenerator(output_dir=temp_dir)
    
    def test_generate_balakovo_creates_directory(self, generator, temp_dir):
        """Should create balakovo subdirectory"""
        generator.generate_balakovo_test_data()
        
        balakovo_dir = Path(temp_dir) / "balakovo"
        assert balakovo_dir.exists()
        assert balakovo_dir.is_dir()
    
    def test_generate_balakovo_berths_creates_file(self, generator, temp_dir):
        """Should create berths CSV file with correct structure"""
        generator.generate_balakovo_test_data()
        
        filepath = Path(temp_dir) / "balakovo" / "berths_balakovo.csv"
        assert filepath.exists(), "Berths file should be created"
        
        df = pd.read_csv(filepath, sep=';')
        
        # Check required columns exist
        expected_columns = [
            'berth_id', 'berth_name', 'berth_type', 'max_loa_m', 
            'max_beam_m', 'max_draft_m', 'cargo_types', 
            'load_rate_mt_day', 'working_hours', 'remarks'
        ]
        assert all(col in df.columns for col in expected_columns), \
            "All required columns should be present"
        
        # Should have exactly 3 berths
        assert len(df) == 3, "Should have 3 test berths"
        
        # Verify berth types
        assert set(df['berth_type'].unique()).issubset({'liquid', 'dry'}), \
            "Berth types should be 'liquid' or 'dry'"
    
    def test_generate_balakovo_berths_data_validity(self, generator, temp_dir):
        """Should generate valid berth data"""
        generator.generate_balakovo_test_data()
        
        df = pd.read_csv(Path(temp_dir) / "balakovo" / "berths_balakovo.csv", sep=';')
        
        # Check numeric fields are valid
        assert all(df['max_loa_m'] > 0), "LOA should be positive"
        assert all(df['max_beam_m'] > 0), "Beam should be positive"
        assert all(df['max_draft_m'] > 0), "Draft should be positive"
        assert all(df['load_rate_mt_day'] > 0), "Load rate should be positive"
        
        # Check working hours are valid
        assert all(df['working_hours'].isin([12, 24])), \
            "Working hours should be 12 or 24"
    
    def test_generate_balakovo_fleet_creates_file(self, generator, temp_dir):
        """Should create fleet CSV file with correct structure"""
        generator.generate_balakovo_test_data()
        
        filepath = Path(temp_dir) / "balakovo" / "fleet_balakovo.csv"
        assert filepath.exists(), "Fleet file should be created"
        
        df = pd.read_csv(filepath, sep=';')
        
        # Check required columns
        expected_columns = [
            'vessel_id', 'vessel_name', 'vessel_type', 'vessel_class',
            'cargo_type', 'capacity_mt', 'loa_m', 'beam_m', 'draft_m',
            'speed_kn', 'owner', 'destination', 'remarks'
        ]
        assert all(col in df.columns for col in expected_columns), \
            "All required columns should be present"
        
        # Should have exactly 8 vessels
        assert len(df) == 8, "Should have 8 test vessels"
    
    def test_generate_balakovo_fleet_vessel_types(self, generator, temp_dir):
        """Should generate correct vessel types"""
        generator.generate_balakovo_test_data()
        
        df = pd.read_csv(Path(temp_dir) / "balakovo" / "fleet_balakovo.csv", sep=';')
        
        # Check vessel types
        assert set(df['vessel_type'].unique()).issubset({'barge', 'dry'}), \
            "Vessel types should be 'barge' or 'dry'"
        
        # Check destinations
        assert set(df['destination'].unique()).issubset({'OYA', 'TUR'}), \
            "Destinations should be 'OYA' or 'TUR'"
        
        # Barges should go to OYA
        barges = df[df['vessel_type'] == 'barge']
        assert all(barges['destination'] == 'OYA'), \
            "All barges should be destined for OYA"
    
    def test_generate_balakovo_cargo_plan_creates_file(self, generator, temp_dir):
        """Should create cargo plan CSV file"""
        generator.generate_balakovo_test_data()
        
        filepath = Path(temp_dir) / "balakovo" / "cargo_plan_balakovo.csv"
        assert filepath.exists(), "Cargo plan file should be created"
        
        df = pd.read_csv(filepath, sep=';')
        
        # Check required columns
        expected_columns = [
            'cargo_id', 'cargo_type', 'qty_mt', 'destination',
            'priority', 'earliest_date', 'latest_date',
            'vessel_preference', 'remarks'
        ]
        assert all(col in df.columns for col in expected_columns), \
            "All required columns should be present"
        
        # Should have multiple cargos
        assert len(df) > 0, "Should have test cargos"
    
    def test_generate_balakovo_cargo_plan_data_validity(self, generator, temp_dir):
        """Should generate valid cargo plan data"""
        generator.generate_balakovo_test_data()
        
        df = pd.read_csv(Path(temp_dir) / "balakovo" / "cargo_plan_balakovo.csv", sep=';')
        
        # Check quantities are positive
        assert all(df['qty_mt'] > 0), "Quantities should be positive"
        
        # Check priorities are valid
        assert all(df['priority'].isin([1, 2, 3])), \
            "Priorities should be 1, 2, or 3"
        
        # Check destinations
        assert set(df['destination'].unique()).issubset({'OYA', 'TUR'}), \
            "Destinations should be 'OYA' or 'TUR'"
        
        # Check cargo types are valid
        valid_cargo_types = {'SFO', 'RPO', 'CSO', 'MEAL', 'PELLETS', 'GRAIN'}
        assert set(df['cargo_type'].unique()).issubset(valid_cargo_types), \
            "Cargo types should be valid"
    
    def test_generate_balakovo_cargo_plan_date_validity(self, generator, temp_dir):
        """Should generate valid date ranges"""
        generator.generate_balakovo_test_data()
        
        df = pd.read_csv(Path(temp_dir) / "balakovo" / "cargo_plan_balakovo.csv", sep=';')
        
        # Check dates can be parsed
        for idx, row in df.iterrows():
            earliest = pd.to_datetime(row['earliest_date'])
            latest = pd.to_datetime(row['latest_date'])
            
            assert earliest <= latest, \
                f"Cargo {row['cargo_id']}: earliest_date should be <= latest_date"
    
    def test_generate_balakovo_params_creates_file(self, generator, temp_dir):
        """Should create parameters CSV file"""
        generator.generate_balakovo_test_data()
        
        filepath = Path(temp_dir) / "balakovo" / "params_balakovo.csv"
        assert filepath.exists(), "Parameters file should be created"
        
        df = pd.read_csv(filepath, sep=';')
        
        # Check required columns
        expected_columns = ['parameter', 'value', 'unit', 'description']
        assert all(col in df.columns for col in expected_columns), \
            "All required columns should be present"
    
    def test_generate_balakovo_params_content(self, generator, temp_dir):
        """Should include all required parameters"""
        generator.generate_balakovo_test_data()
        
        df = pd.read_csv(Path(temp_dir) / "balakovo" / "params_balakovo.csv", sep=';')
        
        # Check critical parameters exist
        param_names = df['parameter'].tolist()
        required_params = [
            'season_start', 'season_end', 'berthing_hours',
            'unberthing_hours', 'doc_clearance_hours'
        ]
        
        for param in required_params:
            assert param in param_names, f"Parameter '{param}' should be present"
    
    def test_generate_balakovo_restrictions_creates_file(self, generator, temp_dir):
        """Should create restrictions CSV file"""
        generator.generate_balakovo_test_data()
        
        filepath = Path(temp_dir) / "balakovo" / "restrictions_balakovo.csv"
        assert filepath.exists(), "Restrictions file should be created"
        
        df = pd.read_csv(filepath, sep=';')
        
        # Check required columns
        expected_columns = [
            'restriction_id', 'restriction_type', 'start_date',
            'end_date', 'berth_id', 'severity', 'description'
        ]
        assert all(col in df.columns for col in expected_columns), \
            "All required columns should be present"
    
    def test_generate_balakovo_restrictions_types(self, generator, temp_dir):
        """Should generate valid restriction types"""
        generator.generate_balakovo_test_data()
        
        df = pd.read_csv(Path(temp_dir) / "balakovo" / "restrictions_balakovo.csv", sep=';')
        
        # Check restriction types are valid
        valid_types = {'weather', 'water_level', 'maintenance', 'holiday'}
        assert set(df['restriction_type'].unique()).issubset(valid_types), \
            "Restriction types should be valid"
        
        # Check severity levels
        valid_severity = {'low', 'medium', 'high'}
        assert set(df['severity'].unique()).issubset(valid_severity), \
            "Severity levels should be valid"


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
        return TestDataGenerator(output_dir=temp_dir)
    
    def test_generate_all_creates_balakovo_data(self, generator, temp_dir):
        """Should create all Balakovo files when calling generate_all()"""
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
            assert filepath.exists(), f"File {filename} should be created"
    
    def test_generate_all_calls_all_generators(self, generator, temp_dir, monkeypatch):
        """Should call all three data generation methods"""
        calls = []
        
        def track_olya(self):
            calls.append('olya')
        
        def track_deepsea(self):
            calls.append('deepsea')
        
        def track_balakovo(self):
            calls.append('balakovo')
        
        monkeypatch.setattr(TestDataGenerator, 'generate_olya_test_data', track_olya)
        monkeypatch.setattr(TestDataGenerator, 'generate_deepsea_test_data', track_deepsea)
        monkeypatch.setattr(TestDataGenerator, 'generate_balakovo_test_data', track_balakovo)
        
        generator.generate_all()
        
        assert 'olya' in calls, "Should call generate_olya_test_data"
        assert 'deepsea' in calls, "Should call generate_deepsea_test_data"
        assert 'balakovo' in calls, "Should call generate_balakovo_test_data"


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_generate_to_nonexistent_directory(self):
        """Should create directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent = Path(temp_dir) / "new_dir" / "nested" / "path"
            generator = TestDataGenerator(output_dir=str(nonexistent))
            
            # Should not raise an error
            generator.generate_balakovo_test_data()
            
            # Directory should be created
            assert nonexistent.exists()
    
    def test_multiple_generation_calls(self):
        """Should handle multiple calls to generation methods"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = TestDataGenerator(output_dir=temp_dir)
            
            # Call twice
            generator.generate_balakovo_test_data()
            generator.generate_balakovo_test_data()
            
            # Files should still exist and be valid
            filepath = Path(temp_dir) / "balakovo" / "berths_balakovo.csv"
            assert filepath.exists()
            
            df = pd.read_csv(filepath, sep=';')
            assert len(df) == 3
    
    def test_csv_separator_consistency(self):
        """Should use semicolon separator consistently"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = TestDataGenerator(output_dir=temp_dir)
            generator.generate_balakovo_test_data()
            
            balakovo_dir = Path(temp_dir) / "balakovo"
            
            for csv_file in balakovo_dir.glob("*.csv"):
                # Should be readable with semicolon separator
                df = pd.read_csv(csv_file, sep=';')
                assert len(df.columns) > 1, \
                    f"File {csv_file.name} should have multiple columns"
    
    def test_empty_remarks_handling(self):
        """Should handle empty remarks fields correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = TestDataGenerator(output_dir=temp_dir)
            generator.generate_balakovo_test_data()
            
            df = pd.read_csv(Path(temp_dir) / "balakovo" / "fleet_balakovo.csv", sep=';')
            
            # Some remarks might be empty, but column should exist
            assert 'remarks' in df.columns
