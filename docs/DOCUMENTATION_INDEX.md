# Documentation Index

Complete guide to all documentation in the Vessel Scheduler System.

**Last Updated**: 2025-12-19
**Version**: 2.1.0

---

## **Documentation Structure**

### Core Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [**README.md**](../README.md) | Main project documentation, overview, and quick start | All users |
| [**QUICK_START.md**](QUICK_START.md) | Step-by-step getting started guide | New users |
| [**WEB_INTERFACES.md**](WEB_INTERFACES.md) | Web interface usage guide | End users |
| [**COMPREHENSIVE_CALCULATION_GUIDE.md**](COMPREHENSIVE_CALCULATION_GUIDE.md) | Complete guide to all calculation methods | Developers, Ops |

### Technical Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [**API_CALCULATION_REFERENCE.md**](API_CALCULATION_REFERENCE.md) | Python API quick reference for calculations | Developers |
| [**BERTH_CONSTRAINTS.md**](BERTH_CONSTRAINTS.md) | Advanced berth constraint system | Developers, Ops |
| [**PHASE2_ENHANCEMENTS.md**](PHASE2_ENHANCEMENTS.md) | Phase 2+ features (PDF, Bunker, RBAC) | Developers |
| [**EXCEL_GANTT_FIX.md**](EXCEL_GANTT_FIX.md) | Excel MergedCell type handling fix | Developers |
| [**UI_ENHANCEMENT_GUIDE.md**](UI_ENHANCEMENT_GUIDE.md) | UI module integration guide | Frontend devs |

### Module Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [**tests/README.md**](../tests/README.md) | Test suite documentation | Developers, QA |
| [**ui_modules/README.md**](../ui_modules/README.md) | Modular UI components guide | Frontend devs |

### Configuration & Standards

| Document | Description | Audience |
|----------|-------------|----------|
| [**.kilocode/rules/rules.md**](../.kilocode/rules/rules.md) | Project coding standards | All developers |
| [**config.yaml**](../config.yaml) | System configuration reference | Ops, Developers |

---

##  Quick Navigation

### I Want To...

#### Get Started
→ Start with [**README.md**](../README.md) then [**QUICK_START.md**](QUICK_START.md)

#### Use Web Interfaces
→ Read [**WEB_INTERFACES.md**](WEB_INTERFACES.md)

#### Configure Berth Constraints
→ See [**BERTH_CONSTRAINTS.md**](BERTH_CONSTRAINTS.md)

#### Understand Phase 2 Features
→ Check [**PHASE2_ENHANCEMENTS.md**](PHASE2_ENHANCEMENTS.md)

#### Develop & Contribute
→ Review [**Project Rules**](../.kilocode/rules/rules.md)

#### Fix Excel Issues
→ See [**EXCEL_GANTT_FIX.md**](EXCEL_GANTT_FIX.md)

#### Integrate UI Modules
→ Read [**UI_ENHANCEMENT_GUIDE.md**](UI_ENHANCEMENT_GUIDE.md) and [**ui_modules/README.md**](../ui_modules/README.md)

#### Run Tests
→ See [**tests/README.md**](../tests/README.md)

#### Learn Calculation Methods
→ Check [**COMPREHENSIVE_CALCULATION_GUIDE.md**](COMPREHENSIVE_CALCULATION_GUIDE.md)

#### Use Calculation APIs
→ See [**API_CALCULATION_REFERENCE.md**](API_CALCULATION_REFERENCE.md)

---

##  Documentation by Role

### For **End Users**
1. [README.md](../README.md) - System overview
2. [QUICK_START.md](QUICK_START.md) - Getting started
3. [WEB_INTERFACES.md](WEB_INTERFACES.md) - Using web interfaces

### For **Developers**
1. [README.md](../README.md) - System architecture
2. [Project Rules](../.kilocode/rules/rules.md) - Coding standards
3. [BERTH_CONSTRAINTS.md](BERTH_CONSTRAINTS.md) - Advanced features
4. [PHASE2_ENHANCEMENTS.md](PHASE2_ENHANCEMENTS.md) - New features
5. [tests/README.md](../tests/README.md) - Testing guide
6. [EXCEL_GANTT_FIX.md](EXCEL_GANTT_FIX.md) - Technical fix documentation
7. [COMPREHENSIVE_CALCULATION_GUIDE.md](COMPREHENSIVE_CALCULATION_GUIDE.md) - Calculation formulas and methods

### For **Operations Team**
1. [QUICK_START.md](QUICK_START.md) - Setup and deployment
2. [WEB_INTERFACES.md](WEB_INTERFACES.md) - Interface usage
3. [BERTH_CONSTRAINTS.md](BERTH_CONSTRAINTS.md) - Constraint configuration
4. [COMPREHENSIVE_CALCULATION_GUIDE.md](COMPREHENSIVE_CALCULATION_GUIDE.md) - Operational calculations

### For **Frontend Developers**
1. [UI_ENHANCEMENT_GUIDE.md](UI_ENHANCEMENT_GUIDE.md) - UI integration
2. [ui_modules/README.md](../ui_modules/README.md) - Modular components
3. [WEB_INTERFACES.md](WEB_INTERFACES.md) - Interface specifications

---

##  Documentation Coverage

### Modules Documented

 **Deep Sea Operations**
- Data structures ([`deepsea_data.py`](../modules/deepsea_data.py))
- Voyage calculation ([`deepsea_calculator.py`](../modules/deepsea_calculator.py))
- Gantt generation ([`deepsea_gantt_excel.py`](../modules/deepsea_gantt_excel.py))
- Scenario management ([`deepsea_scenarios.py`](../modules/deepsea_scenarios.py))

 **Olya (River-Sea) Operations**
- Data structures ([`olya_data.py`](../modules/olya_data.py))
- Calculations ([`olya_calculator.py`](../modules/olya_calculator.py))
- Coordination ([`olya_coordinator.py`](../modules/olya_coordinator.py))
- Gantt visualization ([`olya_gantt_excel.py`](../modules/olya_gantt_excel.py))

 **Balakovo Terminal**
- Data structures ([`balakovo_data.py`](../modules/balakovo_data.py))
- Berth planning ([`balakovo_planner.py`](../modules/balakovo_planner.py))
- Advanced constraints ([`berth_constraints.py`](../modules/berth_constraints.py))
- Gantt generation ([`balakovo_gantt.py`](../modules/balakovo_gantt.py))

 **Phase 2+ Features**
- PDF reporting ([`pdf_reporter.py`](../modules/pdf_reporter.py))
- Bunker optimization ([`bunker_optimizer.py`](../modules/bunker_optimizer.py))
- RBAC system ([`rbac.py`](../modules/rbac.py))
- Enhanced API ([`api_server_enhanced.py`](../api_server_enhanced.py))

 **Utilities**
- Template generation ([`template_generator.py`](../modules/template_generator.py))
- Test data generation ([`test_data_generator.py`](../modules/test_data_generator.py))
- Excel export ([`excel_exporter.py`](../modules/excel_exporter.py))

### Web Interfaces Documented

 [`vessel_scheduler_enhanced.html`](../vessel_scheduler_enhanced.html) - Full-featured scheduler
 [`voyage_planner.html`](../voyage_planner.html) - Voyage calculator (English)
 [`voyage_planner_ru.html`](../voyage_planner_ru.html) - Voyage calculator (Russian)
 UI Modules - Modular components ([`ui_modules`](../ui_modules/))

### Testing Documentation

 Test suite overview ([`tests/README.md`](../tests/README.md))
 59 tests covering all major modules
 Coverage reports and best practices

---

##  Documentation Standards

All documentation follows these principles:

1. **Language**: English (except user-facing Russian interfaces)
2. **Format**: Markdown with proper headers and linking
3. **Examples**: Realistic code examples with explanations
4. **Completeness**: No placeholder text or incomplete sections
5. **Currency**: Updated with version and date stamps
6. **Linking**: Cross-references to related documents
7. **Clarity**: Simple explanations with technical depth

---

##  Documentation Maintenance

### Update Frequency

- **README.md**: Updated with each major release
- **QUICK_START.md**: Updated when installation process changes
- **Feature Docs**: Updated when features are added/modified
- **API Docs**: Updated with each API change
- **Test Docs**: Updated when test suite expands

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.2.0 | 2025-12-19 | Added comprehensive calculation guide |
| 2.1.0 | 2025-12-19 | Removed outdated session summaries and code snippet files |
| 2.0.0 | 2025-12-18 | Complete documentation overhaul |
| 1.1.0 | 2025-12-16 | Added technical fix documentation |
| 1.0.0 | Initial | Initial documentation |

---

##  Contributing to Documentation

When adding or updating documentation:

1. **Follow Standards**: Match existing formatting and style
2. **Add Examples**: Include working code examples
3. **Link Related Docs**: Cross-reference related documentation
4. **Update Index**: Add new documents to this index
5. **Version**: Include version and date information
6. **Test Links**: Verify all links work correctly

---

##  Documentation Support

For documentation questions:
- Check this index for the right document
- Review [**README.md**](../README.md) for overview
- See [**Project Rules**](../.kilocode/rules/rules.md) for standards

---

**Maintained By**: Maritime Logistics Documentation Team
**Last Review**: 2025-12-19
**Next Review**: With next major release
