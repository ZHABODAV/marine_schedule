"""
Tests for Phase 2+ Enhancements

Tests cover:
- PDF Report Generation
- Bunker Optimization
- RBAC (Role-Based Access Control)
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os

# Phase 2+ modules
from modules.pdf_reporter import PDFReportGenerator,  generate_pdf_report
from modules.bunker_optimizer import (
    BunkerOptimizer, BunkerPrice, FuelConsumption, FuelType, BunkerPlan,
    create_sample_bunker_prices, create_sample_fuel_consumption
)
from modules.rbac import (
    RBACManager, User, Role, Permission, UserRole, create_default_admin
)


# ============================================================================
# PDF Reporter Tests
# ============================================================================

class TestPDFReporter:
    """Tests for PDF report generation."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def pdf_generator(self, temp_output_dir):
        """Create PDF generator instance."""
        return PDFReportGenerator(output_dir=temp_output_dir)
    
    @pytest.fixture
    def sample_vessel_data(self):
        """Create sample vessel data."""
        return pd.DataFrame({
            'Vessel ID': ['V001', 'V002', 'V003'],
            'Vessel Name': ['Atlantic Star', 'Pacific Dawn', 'Baltic Sun'],
            'Class': ['Handysize', 'Panamax', 'Handysize'],
            'DWT': [35000, 75000, 38000],
            'Speed': [14.5, 15.0, 14.0]
        })
    
    @pytest.fixture
    def sample_voyage_data(self):
        """Create sample voyage data."""
        return pd.DataFrame({
            'voyage_id': ['V001', 'V002'],
            'vessel_name': ['Atlantic Star', 'Pacific Dawn'],
            'load_port': ['Houston', 'Singapore'],
            'discharge_port': ['Rotterdam', 'Rotterdam'],
            'distance_nm': [4800, 8500],
            'duration_days': [14.5, 25.0],
            'revenue_usd': [350000, 550000],
            'cost_usd': [280000, 420000]
        })
    
    def test_pdf_generator_initialization(self, temp_output_dir):
        """Should initialize PDF generator with output directory."""
        generator = PDFReportGenerator(output_dir=temp_output_dir)
        
        assert generator.output_dir == Path(temp_output_dir)
        assert generator.output_dir.exists()
        assert hasattr(generator, 'styles')
    
    def test_generate_vessel_schedule_report(self, pdf_generator, sample_vessel_data):
        """Should generate vessel schedule PDF report."""
        filepath = pdf_generator.generate_vessel_schedule_report(
            vessel_data=sample_vessel_data,
            filename="test_vessel_schedule.pdf",
            title="Test Vessel Schedule"
        )
        
        assert os.path.exists(filepath)
        assert filepath.endswith('.pdf')
        assert os.path.getsize(filepath) > 0
    
    def test_generate_voyage_summary_report(self, pdf_generator, sample_voyage_data):
        """Should generate voyage summary PDF report."""
        filepath = pdf_generator.generate_voyage_summary_report(
            voyage_data=sample_voyage_data,
            filename="test_voyage_summary.pdf",
            include_financials=True
        )
        
        assert os.path.exists(filepath)
        assert filepath.endswith('.pdf')
        assert os.path.getsize(filepath) > 0
    
    def test_generate_fleet_overview_report(self, pdf_generator, sample_vessel_data):
        """Should generate fleet overview PDF report."""
        filepath = pdf_generator.generate_fleet_overview_report(
            fleet_data=sample_vessel_data,
            filename="test_fleet_overview.pdf"
        )
        
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0
    
    def test_convenience_function(self, temp_output_dir, sample_vessel_data):
        """Should generate PDF using convenience function."""
        filepath = generate_pdf_report(
            report_type='vessel_schedule',
            data=sample_vessel_data,
            output_dir=temp_output_dir,
            filename="convenience_test.pdf"
        )
        
        assert os.path.exists(filepath)


# ============================================================================
# Bunker Optimizer Tests
# ============================================================================

class TestBunkerOptimizer:
    """Tests for bunker optimization."""
    
    @pytest.fixture
    def bunker_prices(self):
        """Create sample bunker prices."""
        return create_sample_bunker_prices()
    
    @pytest.fixture
    def fuel_consumption_params(self):
        """Create sample fuel consumption parameters."""
        return {
            'vessel_1': create_sample_fuel_consumption('vessel_1'),
            'vessel_2': create_sample_fuel_consumption('vessel_2')
        }
    
    @pytest.fixture
    def optimizer(self, bunker_prices, fuel_consumption_params):
        """Create bunker optimizer instance."""
        return BunkerOptimizer(bunker_prices, fuel_consumption_params)
    
    def test_optimizer_initialization(self, optimizer, bunker_prices):
        """Should initialize optimizer with prices and parameters."""
        assert len(optimizer.bunker_prices) == len(bunker_prices)
        assert len(optimizer.price_index) > 0
        assert isinstance(optimizer.fuel_consumption_params, dict)
    
    def test_optimize_bunker_plan(self, optimizer):
        """Should create optimized bunker plan."""
        plan = optimizer.optimize_bunker_plan(
            voyage_id="V001",
            vessel_id="vessel_1",
            route_ports=["SINGAPORE", "GIBRALTAR", "ROTTERDAM"],
            distances_nm=[3500, 1500],
            port_times_days=[1, 0.5],
            fuel_type=FuelType.VLSFO,
            current_fuel_mt=500,
            allow_eco_speed=True
        )
        
        assert isinstance(plan, BunkerPlan)
        assert plan.voyage_id == "V001"
        assert plan.vessel_id == "vessel_1"
        assert plan.total_consumption_mt > 0
        assert plan.total_cost_usd > 0
        assert isinstance(plan.bunker_stops, list)
    
    def test_fuel_consumption_calculation(self):
        """Should calculate fuel consumption correctly."""
        fuel_params = create_sample_fuel_consumption('test_vessel')
        
        consumption = fuel_params.calculate_voyage_consumption(
            distance_nm=1000,
            speed_kts=14.5,
            port_time_days=2
        )
        
        assert consumption > 0
        # Sea time: 1000 / (14.5 * 24) ≈ 2.87 days
        # Sea consumption: 2.87 * 35 ≈ 100 MT
        # Port consumption: 2 * 5 = 10 MT
        # Total ≈ 110 MT
        assert 100 < consumption < 120
    
    def test_fuel_savings_calculation(self):
        """Should calculate fuel savings from eco-speed."""
        fuel_params = create_sample_fuel_consumption('test_vessel')
        
        savings = fuel_params.calculate_fuel_savings(distance_nm=5000)
        
        assert 'normal_consumption_mt' in savings
        assert 'eco_consumption_mt' in savings
        assert 'fuel_savings_mt' in savings
        assert 'time_difference_days' in savings
        assert savings['fuel_savings_mt'] > 0
    
    def test_find_cheapest_bunker_port(self, optimizer):
        """Should find cheapest port for bunkering."""
        cheapest = optimizer.find_cheapest_bunker_port(
            fuel_type=FuelType.VLSFO,
            quantity_mt=1000,
            ports=["SINGAPORE", "ROTTERDAM", "FUJAIRAH"]
        )
        
        assert cheapest is not None
        assert isinstance(cheapest, BunkerPrice)
        assert cheapest.fuel_type == FuelType.VLSFO
        assert cheapest.availability_mt >= 1000
    
    def test_bunker_market_analysis(self, optimizer):
        """Should analyze bunker market."""
        analysis = optimizer.analyze_bunker_market(FuelType.VLSFO)
        
        assert 'fuel_type' in analysis
        assert 'average_price' in analysis
        assert 'min_price' in analysis
        assert 'max_price' in analysis
        assert 'price_spread' in analysis
        assert 'cheapest_port' in analysis
        assert analysis['average_price'] > 0
    
    def test_hedging_position_calculation(self, optimizer):
        """Should calculate hedging position."""
        hedging = optimizer.calculate_hedging_position(
            total_consumption_mt=10000,
            fuel_type=FuelType.VLSFO,
            hedge_percentage=0.7
        )
        
        assert 'hedge_volume_mt' in hedging
        assert 'hedge_value_usd' in hedging
        assert 'average_price' in hedging
        assert 'value_at_risk_95_usd' in hedging
        assert hedging['hedge_volume_mt'] == 7000  # 70% of 10000


# ============================================================================
# RBAC Tests
# ============================================================================

class TestRBAC:
    """Tests for Role-Based Access Control."""
    
    @pytest.fixture
    def temp_rbac_dir(self):
        """Create temporary RBAC data directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def rbac_manager(self, temp_rbac_dir):
        """Create RBAC manager instance."""
        return RBACManager(data_dir=temp_rbac_dir)
    
    def test_rbac_initialization(self, rbac_manager):
        """Should initialize RBAC with default roles."""
        assert len(rbac_manager.roles) > 0
        assert UserRole.ADMIN.value in rbac_manager.roles
        assert UserRole.SCHEDULER.value in rbac_manager.roles
        assert UserRole.VIEWER.value in rbac_manager.roles
    
    def test_create_user(self, rbac_manager):
        """Should create new user with roles."""
        user = rbac_manager.create_user(
            username="test_user",
            password="test_password",
            email="test@example.com",
            full_name="Test User",
            role_names=[UserRole.SCHEDULER.value],
            department="Operations"
        )
        
        assert isinstance(user, User)
        assert user.username == "test_user"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.department == "Operations"
        assert len(user.roles) == 1
        assert user.roles[0].role_id == UserRole.SCHEDULER.value
    
    def test_duplicate_user_creation(self, rbac_manager):
        """Should raise error when creating duplicate user."""
        rbac_manager.create_user(
            username="duplicate",
            password="password",
            email="dup@example.com",
            full_name="Duplicate User",
            role_names=[UserRole.VIEWER.value]
        )
        
        with pytest.raises(ValueError, match="already exists"):
            rbac_manager.create_user(
                username="duplicate",
                password="another_password",
                email="dup2@example.com",
                full_name="Another User",
                role_names=[UserRole.VIEWER.value]
            )
    
    def test_authentication_success(self, rbac_manager):
        """Should authenticate user with correct credentials."""
        rbac_manager.create_user(
            username="auth_user",
            password="correct_password",
            email="auth@example.com",
            full_name="Auth User",
            role_names=[UserRole.VIEWER.value]
        )
        
        token = rbac_manager.authenticate("auth_user", "correct_password")
        
        assert token is not None
        assert len(token) > 0
    
    def test_authentication_failure(self, rbac_manager):
        """Should fail authentication with wrong password."""
        rbac_manager.create_user(
            username="auth_fail_user",
            password="correct_password",
            email="authfail@example.com",
            full_name="Auth Fail User",
            role_names=[UserRole.VIEWER.value]
        )
        
        token = rbac_manager.authenticate("auth_fail_user", "wrong_password")
        
        assert token is None
    
    def test_token_validation(self, rbac_manager):
        """Should validate active token."""
        rbac_manager.create_user(
            username="token_user",
            password="password",
            email="token@example.com",
            full_name="Token User",
            role_names=[UserRole.SCHEDULER.value]
        )
        
        token = rbac_manager.authenticate("token_user", "password")
        user = rbac_manager.validate_token(token)
        
        assert user is not None
        assert user.username == "token_user"
    
    def test_token_expiration(self, rbac_manager):
        """Should invalidate expired token."""
        user = rbac_manager.create_user(
            username="expire_user",
            password="password",
            email="expire@example.com",
            full_name="Expire User",
            role_names=[UserRole.VIEWER.value]
        )
        
        token = rbac_manager.authenticate("expire_user", "password")
        
        # Manually expire token
        user.token_expires = datetime.now() - timedelta(hours=1)
        
        validated_user = rbac_manager.validate_token(token)
        assert validated_user is None
    
    def test_permission_check(self, rbac_manager):
        """Should check user permissions correctly."""
        rbac_manager.create_user(
            username="perm_user",
            password="password",
            email="perm@example.com",
            full_name="Permission User",
            role_names=[UserRole.SCHEDULER.value]
        )
        
        token = rbac_manager.authenticate("perm_user", "password")
        
        # Scheduler should have these permissions
        assert rbac_manager.check_permission(token, Permission.VIEW_VESSELS)
        assert rbac_manager.check_permission(token, Permission.CREATE_SCHEDULES)
        
        # Scheduler should NOT have admin permissions
        assert not rbac_manager.check_permission(token, Permission.MANAGE_USERS)
    
    def test_admin_permissions(self, rbac_manager, monkeypatch):
        """Should grant all permissions to admin role."""
        # Ensure the default admin password is deterministic for the test.
        monkeypatch.setenv("RBAC_DEFAULT_ADMIN_PASSWORD", "admin_test_password")

        create_default_admin(rbac_manager)
        token = rbac_manager.authenticate("admin", "admin_test_password")

        # Admin should have all permissions
        for permission in Permission:
            assert rbac_manager.check_permission(token, permission)
    
    def test_logout(self, rbac_manager):
        """Should invalidate token on logout."""
        rbac_manager.create_user(
            username="logout_user",
            password="password",
            email="logout@example.com",
            full_name="Logout User",
            role_names=[UserRole.VIEWER.value]
        )
        
        token = rbac_manager.authenticate("logout_user", "password")
        assert rbac_manager.validate_token(token) is not None
        
        rbac_manager.logout(token)
        assert rbac_manager.validate_token(token) is None
    
    def test_audit_logging(self, rbac_manager):
        """Should log actions to audit trail."""
        initial_log_count = len(rbac_manager.audit_logs)
        
        rbac_manager.create_user(
            username="audit_user",
            password="password",
            email="audit@example.com",
            full_name="Audit User",
            role_names=[UserRole.VIEWER.value]
        )
        
        # Should have logged user creation
        assert len(rbac_manager.audit_logs) > initial_log_count
        
        # Authenticate (should log login)
        rbac_manager.authenticate("audit_user", "password")
        
        # Should have logged login
        assert len(rbac_manager.audit_logs) > initial_log_count + 1
    
    def test_user_has_permission(self,rbac_manager):
        """Should check if user has specific permission."""
        user = rbac_manager.create_user(
            username="has_perm_user",
            password="password",
            email="hasperm@example.com",
            full_name="Has Permission User",
            role_names=[UserRole.FINANCE_MANAGER.value]
        )
        
        assert user.has_permission(Permission.VIEW_FINANCIALS)
        assert user.has_permission(Permission.VIEW_VESSELS)
        assert not user.has_permission(Permission.DELETE_VESSELS)
    
    def test_password_hashing(self):
        """Should hash passwords securely (salted) and verify correctly."""
        password = "secure_password_123"
        hash1 = RBACManager.hash_password(password)
        hash2 = RBACManager.hash_password(password)

        # Salted hashing => same password should not produce the same hash.
        assert hash1 != hash2

        # Hash should not be the password itself
        assert hash1 != password

        # Verification should succeed
        assert RBACManager.verify_password(password, hash1)
        assert RBACManager.verify_password(password, hash2)

        # Wrong password should fail
        assert not RBACManager.verify_password("wrong_password", hash1)


# ============================================================================
# Integration Tests
# ============================================================================

class TestPhase2Integration:
    """Integration tests for Phase 2+ features."""
    
    def test_pdf_and_bunker_integration(self, tmp_path):
        """Should generate PDF report with bunker optimization results."""
        # Create bunker plan
        optimizer = BunkerOptimizer(
            create_sample_bunker_prices(),
            {'vessel_1': create_sample_fuel_consumption('vessel_1')}
        )
        
        plan = optimizer.optimize_bunker_plan(
            voyage_id="INT_V001",
            vessel_id="vessel_1",
            route_ports=["SINGAPORE", "ROTTERDAM"],
            distances_nm=[5000],
            port_times_days=[2],
            fuel_type=FuelType.VLSFO,
            current_fuel_mt=1000,
            allow_eco_speed=True
        )
        
        # Create DataFrame from bunker plan
        bunker_df = pd.DataFrame([{
            'Voyage ID': plan.voyage_id,
            'Total Consumption (MT)': plan.total_consumption_mt,
            'Total Cost (USD)': plan.total_cost_usd,
            'Savings (USD)': plan.savings_vs_baseline_usd
        }])
        
        # Generate PDF
        pdf_gen = PDFReportGenerator(output_dir=str(tmp_path))
        filepath = pdf_gen.generate_custom_report(
            data_sections=[{'title': 'Bunker Optimization Results', 'data': bunker_df}],
            title="Integrated Bunker Report",
            filename="integrated_test.pdf"
        )
        
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0
