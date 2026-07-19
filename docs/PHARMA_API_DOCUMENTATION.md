# Pharmaceutical Compliance API Documentation

## Overview

This document provides comprehensive API documentation for the pharmaceutical compliance features implemented in the Omnexa Trading application.

## Base URL

```
/api/method/omnexa_trading
```

## Authentication

All API endpoints require Frappe session authentication. Ensure you have a valid session before making API calls.

## Batch Management APIs

### 1. Validate Batch for Sale

Validates if a batch is valid for sale based on expiry, quality status, and regulatory compliance.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch.validate_batch_for_sale`

**Method:** POST

**Parameters:**
- `batch_no` (string): Batch number to validate

**Response:**
```json
{
  "valid": true,
  "message": "Batch is valid for sale"
}
```

### 2. Get FEFO Batches

Retrieves batches for an item using First Expired, First Out (FEFO) logic.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch.get_fefo_batches`

**Method:** GET

**Parameters:**
- `item_code` (string): Item code
- `warehouse` (string, optional): Warehouse filter
- `qty` (integer, optional): Required quantity

**Response:**
```json
[
  {
    "name": "batch-001",
    "batch_number": "BATCH-001",
    "item_code": "ITEM-001",
    "expiry_date": "2026-12-31",
    "days_until_expiry": 180,
    "quality_status": "Approved",
    "is_active": 1,
    "available_qty": 100
  }
]
```

### 3. Get FIFO Batches

Retrieves batches for an item using First In, First Out (FIFO) logic.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch.get_fifo_batches`

**Method:** GET

**Parameters:**
- `item_code` (string): Item code
- `warehouse` (string, optional): Warehouse filter
- `qty` (integer, optional): Required quantity

**Response:** Same as FEFO batches

### 4. Suggest Batch for Picking

Suggests the optimal batch for picking based on strategy.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch.suggest_batch_for_picking`

**Method:** GET

**Parameters:**
- `item_code` (string): Item code
- `warehouse` (string, optional): Warehouse filter
- `qty` (integer, optional): Required quantity
- `picking_strategy` (string): "FEFO" or "FIFO"

**Response:**
```json
{
  "name": "batch-001",
  "batch_number": "BATCH-001",
  "available_qty": 100
}
```

### 5. Quarantine Batch

Places a batch in quarantine.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch.quarantine_batch`

**Method:** POST

**Parameters:**
- `batch_no` (string): Batch number
- `quarantine_reason` (string): Reason for quarantine

**Response:**
```json
{
  "success": true,
  "message": "Batch BATCH-001 placed in quarantine"
}
```

### 6. Release Quarantined Batch

Releases a batch from quarantine.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch.release_quarantined_batch`

**Method:** POST

**Parameters:**
- `batch_no` (string): Batch number
- `release_reason` (string): Reason for release

**Response:**
```json
{
  "success": true,
  "message": "Batch BATCH-001 released from quarantine"
}
```

### 7. Get Batch Stock Summary

Retrieves stock summary for a batch across warehouses.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch.get_batch_stock_summary`

**Method:** GET

**Parameters:**
- `batch_no` (string): Batch number

**Response:**
```json
{
  "warehouse_stock": [
    {
      "warehouse": "Warehouse-001",
      "actual_qty": 50,
      "projected_qty": 50,
      "reserved_qty": 0
    }
  ],
  "total_actual_qty": 50,
  "total_projected_qty": 50,
  "total_reserved_qty": 0
}
```

### 8. Get Batch Movement History

Retrieves movement history for a batch.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_batch.pharma_batch.get_batch_movement_history`

**Method:** GET

**Parameters:**
- `batch_no` (string): Batch number
- `limit` (integer, optional): Number of records (default: 50)

**Response:**
```json
[
  {
    "name": "SLE-001",
    "posting_date": "2026-07-05",
    "posting_time": "10:00:00",
    "voucher_type": "Sales Invoice",
    "voucher_no": "INV-001",
    "warehouse": "Warehouse-001",
    "actual_qty": -10,
    "qty_after_transaction": 90
  }
]
```

## Quality Control APIs

### 1. Create Quality Inspection from Batch

Creates a quality inspection for a batch.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_quality_inspection.pharma_quality_inspection.create_inspection_from_batch`

**Method:** POST

**Parameters:**
- `batch_no` (string): Batch number
- `inspection_type` (string): Inspection type (Incoming, Outgoing, Internal)

**Response:**
```json
{
  "inspection_name": "QI-20260705-001"
}
```

### 2. Get Pending Inspections

Retrieves pending quality inspections.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_quality_inspection.pharma_quality_inspection.get_pending_inspections`

**Method:** GET

**Parameters:**
- `company` (string, optional): Company filter

**Response:**
```json
[
  {
    "name": "QI-001",
    "inspection_number": "QI-20260705-001",
    "item_code": "ITEM-001",
    "batch_number": "BATCH-001",
    "inspection_status": "Pending"
  }
]
```

## Audit Trail APIs

### 1. Log Audit Event

Logs an audit event.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.audit_log.audit_log.log_audit_event`

**Method:** POST

**Parameters:**
- `action` (string): Action (Create, Update, Delete, Submit, Cancel)
- `document_type` (string): Document type
- `document_name` (string): Document name
- `change_reason` (string, optional): Reason for change

**Response:**
```json
{
  "log_name": "AUDIT-20260705-001"
}
```

### 2. Get Audit Trail

Retrieves audit trail for a document.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.audit_log.audit_log.get_audit_trail`

**Method:** GET

**Parameters:**
- `document_type` (string): Document type
- `document_name` (string): Document name

**Response:**
```json
[
  {
    "name": "AUDIT-001",
    "log_id": "AUDIT-20260705-001",
    "timestamp": "2026-07-05 10:00:00",
    "user": "admin@example.com",
    "action": "Create",
    "document_type": "Pharma Batch",
    "document_name": "BATCH-001"
  }
]
```

### 3. Get User Activity Logs

Retrieves activity logs for a user.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.audit_log.audit_log.get_user_activity_logs`

**Method:** GET

**Parameters:**
- `user` (string): User email
- `from_date` (string, optional): Start date
- `to_date` (string, optional): End date

**Response:**
```json
[
  {
    "name": "AUDIT-001",
    "action": "Create",
    "document_type": "Pharma Batch",
    "timestamp": "2026-07-05 10:00:00"
  }
]
```

## Cold Chain Management APIs

### 1. Get Temperature Logs

Retrieves temperature logs for a batch.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.temperature_log.temperature_log.get_temperature_logs`

**Method:** GET

**Parameters:**
- `batch_no` (string): Batch number
- `from_date` (string, optional): Start date
- `to_date` (string, optional): End date

**Response:**
```json
[
  {
    "name": "TEMP-001",
    "log_number": "TEMP-20260705-001",
    "log_date": "2026-07-05",
    "log_time": "10:00:00",
    "temperature": 5.0,
    "temperature_status": "Normal",
    "excursion_flag": 0
  }
]
```

### 2. Get Temperature Summary

Retrieves temperature summary for a batch.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.temperature_log.temperature_log.get_temperature_summary`

**Method:** GET

**Parameters:**
- `batch_no` (string): Batch number

**Response:**
```json
{
  "avg_temp": 5.5,
  "min_temp": 2.0,
  "max_temp": 8.0,
  "total_logs": 100
}
```

### 3. Get Open Excursions

Retrieves open temperature excursions.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.temperature_excursion.temperature_excursion.get_open_excursions`

**Method:** GET

**Response:**
```json
[
  {
    "name": "EXC-001",
    "excursion_number": "EXC-20260705-001",
    "excursion_date": "2026-07-05",
    "batch_number": "BATCH-001",
    "severity": "Major",
    "temperature": 15.0
  }
]
```

### 4. Resolve Excursion

Resolves a temperature excursion.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.temperature_excursion.temperature_excursion.resolve_excursion`

**Method:** POST

**Parameters:**
- `excursion_name` (string): Excursion name
- `resolution_notes` (string): Resolution notes
- `disposition` (string): Disposition (Release, Quarantine, Destroy, Return)

**Response:**
```json
{
  "success": true,
  "message": "Excursion EXC-20260705-001 resolved"
}
```

## Controlled Substances APIs

### 1. Create Regulatory Approval

Creates regulatory approval for a controlled substance batch.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_regulatory_approval.pharma_regulatory_approval.create_regulatory_approval`

**Method:** POST

**Parameters:**
- `batch_no` (string): Batch number
- `controlled_substance_type` (string): Type (Narcotic, Psychotropic, Precursor, Other)
- `license_number` (string): License number
- `license_expiry` (string): License expiry date

**Response:**
```json
{
  "approval_name": "REG-20260705-001"
}
```

### 2. Validate Controlled Substance Sale

Validates if controlled substance sale is allowed.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_regulatory_approval.pharma_regulatory_approval.validate_controlled_substance_sale`

**Method:** POST

**Parameters:**
- `batch_no` (string): Batch number
- `quantity` (float): Quantity to sell

**Response:**
```json
{
  "valid": true,
  "message": "Controlled substance sale is valid"
}
```

## Product Recall APIs

### 1. Initiate Product Recall

Initiates a product recall for a batch.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_product_recall.pharma_product_recall.initiate_product_recall`

**Method:** POST

**Parameters:**
- `batch_no` (string): Batch number
- `recall_reason` (string): Recall reason
- `recall_type` (string): Recall type (Voluntary, Mandatory)
- `severity` (string): Severity level

**Response:**
```json
{
  "recall_name": "REC-20260705-001"
}
```

### 2. Notify Customers

Notifies affected customers about product recall.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_product_recall.pharma_product_recall.notify_customers`

**Method:** POST

**Parameters:**
- `recall_name` (string): Recall name

**Response:**
```json
{
  "success": true,
  "message": "Customer notifications sent"
}
```

### 3. Complete Recall

Completes a product recall.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.pharma_product_recall.pharma_product_recall.complete_recall`

**Method:** POST

**Parameters:**
- `recall_name` (string): Recall name
- `resolution_plan` (string): Resolution plan
- `corrective_actions` (string): Corrective actions

**Response:**
```json
{
  "success": true,
  "message": "Recall REC-20260705-001 completed"
}
```

## Security APIs

### 1. Check Field Permission

Checks if a user has permission to access a field.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.field_permission.field_permission.check_field_permission`

**Method:** GET

**Parameters:**
- `doctype` (string): DocType name
- `field_name` (string): Field name
- `user` (string, optional): User email (defaults to current user)

**Response:**
```json
{
  "read": true,
  "write": false,
  "mask": false,
  "hide": false
}
```

### 2. Mask Field Value

Masks field value based on field permissions.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.field_permission.field_permission.mask_field_value`

**Method:** POST

**Parameters:**
- `doctype` (string): DocType name
- `field_name` (string): Field name
- `value` (string): Field value
- `user` (string, optional): User email

**Response:**
```json
"****1234"
```

## Encryption APIs

### 1. Generate Encryption Key

Generates a new encryption key.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.encryption_key.encryption_key.generate_encryption_key`

**Method:** GET

**Parameters:**
- `algorithm` (string): Algorithm (AES, RSA, Fernet)
- `key_length` (integer): Key length in bits

**Response:**
```json
"generated_key_string"
```

### 2. Encrypt Data

Encrypts data using specified encryption key.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.encryption_key.encryption_key.encrypt_data`

**Method:** POST

**Parameters:**
- `data` (string): Data to encrypt
- `key_name` (string): Name of encryption key

**Response:**
```json
"encrypted_data_string"
```

### 3. Decrypt Data

Decrypts data using specified encryption key.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.encryption_key.encryption_key.decrypt_data`

**Method:** POST

**Parameters:**
- `encrypted_data` (string): Data to decrypt
- `key_name` (string): Name of encryption key

**Response:**
```json
"decrypted_data_string"
```

### 4. Rotate Key

Rotates encryption key.

**Endpoint:** `/api/method/omnexa_trading.omnexa_trading.doctype.encryption_key.encryption_key.rotate_key`

**Method:** POST

**Parameters:**
- `key_name` (string): Name of key to rotate

**Response:**
```json
{
  "new_key_name": "KEY-20260705-ROTATED-20260705"
}
```

## Error Handling

All API endpoints return appropriate HTTP status codes and error messages:

- **200**: Success
- **400**: Bad Request (invalid parameters)
- **401**: Unauthorized (authentication required)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found (resource not found)
- **500**: Internal Server Error

Error response format:
```json
{
  "error": {
    "message": "Error description",
    "code": "ERROR_CODE"
  }
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse. Default limit: 1000 requests per hour per user.

## Versioning

Current API version: v1.0

Include version in request header:
```
X-API-Version: v1.0
```

## Support

For API support and questions, contact the development team at:
- Email: dev@omnexa.com
- Documentation: https://docs.omnexa.com
