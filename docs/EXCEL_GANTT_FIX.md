# Excel Gantt Chart - MergedCell Fix Documentation

## Issue Overview

**Problem**: Pylance type checker error when attempting to assign values to Excel cells
**Location**: [`modules/deepsea_gantt_excel.py:277`](../modules/deepsea_gantt_excel.py:277)
**Error**: `Cannot assign to attribute "value" for class "MergedCell" - "str" is not assignable to "None"`

## Root Cause

When working with the `openpyxl` library, merged cells behave differently from regular cells:

- **Regular Cell**: Has a writable `value` attribute that can be set to any value
- **MergedCell**: Represents cells that are part of a merged range (but not the top-left cell)
  - Has a read-only `value` attribute that is always `None`
  - Cannot have its value, font, or alignment modified directly

### Why This Happens

In the Excel Gantt generation code, cells are merged in row 1 for the title (line 141):
```python
ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=min(15, days_in_month + 4))
```

While the data cells themselves aren't merged, openpyxl's type system requires checking whether a cell is a `MergedCell` before attempting to modify it, especially when working with dynamically generated spreadsheets.

## Solution Implemented

### 1. Import MergedCell Type
**File**: [`modules/deepsea_gantt_excel.py:15`](../modules/deepsea_gantt_excel.py:15)

```python
from openpyxl.cell.cell import MergedCell
```

This import provides access to the `MergedCell` class for type checking.

### 2. Add Type Check Before Cell Modification
**File**: [`modules/deepsea_gantt_excel.py:278-283`](../modules/deepsea_gantt_excel.py:278)

```python
# Проверяем, что ячейка не является частью объединённого диапазона
if not isinstance(cell, MergedCell):
    cell.value = abbrev
    cell.font = Font(size=7, bold=True, 
                   color='FFFFFF' if fill_key != 'sea_ballast' else '000000')
    cell.alignment = Alignment(horizontal='center', vertical='center')
```

**What This Does**:
- Checks if the cell is NOT a `MergedCell` instance
- Only sets properties (value, font, alignment) on regular cells
- Prevents runtime errors when encountering merged cells

## Code Context

The fix is applied in the `generate_month()` method where it:

1. **Iterates through days** of the month (line 245)
2. **Creates a cell** for each day in the Gantt chart (line 250)
3. **Finds matching voyage legs** for each day (lines 259-281)
4. **Sets cell properties** based on the leg type and cargo state

The problematic code was attempting to set `cell.value = abbrev` without checking if the cell was writable.

## Best Practices for openpyxl

### When Working with Merged Cells

1. **Always check the cell type** before modification:
   ```python
   if not isinstance(cell, MergedCell):
       cell.value = "Some value"
   ```

2. **Only modify the top-left cell** of a merged range:
   ```python
   ws.merge_cells('A1:C1')
   ws['A1'].value = "Title"  #  Correct
   ws['B1'].value = "Title"  #  Error - B1 is now a MergedCell
   ```

3. **Get the top-left cell** of a merged range if needed:
   ```python
   from openpyxl.cell.cell import MergedCell
   
   if isinstance(cell, MergedCell):
       # Find the merged range and use its top-left cell
       for merged_range in ws.merged_cells.ranges:
           if cell.coordinate in merged_range:
               top_left = ws.cell(merged_range.min_row, merged_range.min_col)
               top_left.value = "Value"
               break
   ```

### Type Safety with Pylance/Mypy

The type checker needs explicit checks because:
- `ws.cell()` can return either `Cell` or `MergedCell`
- `MergedCell.value` is typed as `None` (read-only)
- Attempting to assign to it violates type safety

## Testing the Fix

### Verify the Fix Works

1. **Run the Deep Sea scheduler**:
   ```bash
   python main_deepsea.py
   ```

2. **Check for errors** in the Excel generation output

3. **Open generated files** in `output/deepsea/`:
   - `gantt_deepsea_YYYY_MM.xlsx` - Monthly Gantt charts
   - `fleet_overview.xlsx` - Fleet utilization overview

### What to Look For

 **Success indicators**:
- Files generated without errors
- Cell values populated correctly (L, D, →, ⟶, C, B)
- Formatting applied (colors, fonts, alignment)
- No Pylance warnings in the code

 **Failure indicators**:
- Runtime errors about MergedCell
- Empty cells in the Gantt chart
- Type checker warnings

## Related Files

- [`modules/deepsea_gantt_excel.py`](../modules/deepsea_gantt_excel.py) - Deep Sea Gantt Excel generator
- [`modules/olya_gantt_excel.py`](../modules/olya_gantt_excel.py) - Olya Gantt Excel generator (may need similar fix)
- [`modules/excel_exporter.py`](../modules/excel_exporter.py) - General Excel export utilities

## Additional Notes

### Performance Consideration
The `isinstance()` check is extremely fast (O(1)) and adds negligible overhead. It's a small price to pay for type safety and preventing runtime errors.

### Alternative Approaches

1. **Avoid merging cells** in data areas (current code already does this)
2. **Type cast** to ignore the warning (NOT recommended):
   ```python
   cell.value = abbrev  # type: ignore
   ```
3. **Use try-except** (NOT recommended - less clear):
   ```python
   try:
       cell.value = abbrev
   except AttributeError:
       pass
   ```

The implemented solution (type checking) is the **cleanest and most explicit** approach.

## Summary

| Aspect | Details |
|--------|---------|
| **Problem** | Cannot assign to `MergedCell.value` |
| **Cause** | openpyxl returns `MergedCell` for cells in merged ranges |
| **Solution** | Type check with `isinstance(cell, MergedCell)` |
| **Impact** | Fixes Pylance error, prevents runtime errors |
| **Files Changed** | `modules/deepsea_gantt_excel.py` (2 locations) |

---

**Last Updated**: 2025-12-16  
**Author**: Kilo Code  
**Related Issue**: Pylance type checking for openpyxl cells
