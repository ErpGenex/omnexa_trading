# Pharmaceutical Compliance User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Batch Management](#batch-management)
3. [Expiry Management](#expiry-management)
4. [Quality Control](#quality-control)
5. [Cold Chain Management](#cold-chain-management)
6. [Controlled Substances](#controlled-substances)
7. [Product Recall](#product-recall)
8. [Audit Trail](#audit-trail)
9. [Security Features](#security-features)
10. [Troubleshooting](#troubleshooting)

## Introduction

This user guide provides comprehensive instructions for using the pharmaceutical compliance features in the Omnexa Trading system. These features are designed to help pharmaceutical trading and distribution companies maintain regulatory compliance and ensure product safety.

### Key Features

- **Batch Management**: Track pharmaceutical batches with full traceability
- **Expiry Management**: Monitor and manage product expiry dates
- **Quality Control**: Conduct quality inspections and maintain quality standards
- **Cold Chain Management**: Monitor temperature-sensitive products
- **Controlled Substances**: Manage regulatory approvals for controlled substances
- **Product Recall**: Initiate and manage product recalls
- **Audit Trail**: Track all system activities for compliance
- **Security**: Field-level permissions and data encryption

## Batch Management

### Creating a New Batch

1. Navigate to **Pharma Batch** from the main menu
2. Click **New** to create a new batch
3. Fill in the required fields:
   - **Batch Number**: Unique identifier for the batch
   - **Item Code**: Select the pharmaceutical item
   - **Manufacturing Date**: Date of manufacture
   - **Expiry Date**: Product expiry date
   - **Total Quantity**: Quantity in the batch
   - **Warehouse**: Storage location
   - **Company**: Your company
4. Set additional parameters:
   - **Quality Status**: Initial quality status (Pending/Approved/Quarantined)
   - **Is Active**: Whether the batch is active
   - **Cold Chain Required**: If the product requires cold chain
   - **Storage Temperature**: Required storage conditions
   - **Controlled Substance Flag**: If it's a controlled substance
5. Click **Save** to create the batch
6. Click **Submit** to activate the batch

### Viewing Batch Information

1. Navigate to **Pharma Batch** list
2. Click on any batch to view details
3. The batch view shows:
   - Basic information (dates, quantities, status)
   - Quality information (inspection status, quality hold)
   - Regulatory information (approvals, licenses)
   - Stock information (warehouse quantities)
   - Movement history

### Batch Validation

The system automatically validates batches for:
- Expiry dates (cannot be before manufacturing date)
- Batch number uniqueness
- Required fields completion
- Quality status compliance

### Batch Quarantine

To quarantine a batch:

1. Open the batch record
2. Click **Quarantine Batch** button
3. Enter the reason for quarantine
4. Click **Confirm**

The batch will be marked as quarantined and cannot be used in sales.

### Batch Release

To release a quarantined batch:

1. Open the batch record
2. Click **Release Batch** button
3. Enter the release reason
4. Click **Confirm**

The batch will be released and available for use.

## Expiry Management

### Expiry Blocking in Sales

The system automatically blocks sales of expired batches:
- Expired batches cannot be selected in sales invoices
- Near-expiry batches (less than 30 days) show warnings
- System validates expiry before invoice submission

### FEFO/FIFO Picking

The system supports two picking strategies:

**FEFO (First Expired, First Out)**:
- Prioritizes batches with earliest expiry dates
- Recommended for products with limited shelf life
- Minimizes expiry losses

**FIFO (First In, First Out)**:
- Prioritizes batches with earliest manufacturing dates
- Recommended for products with long shelf life
- Follows standard inventory practices

To use batch picking:
1. In sales invoice, select the item
2. Click **Suggest Batch** button
3. Select picking strategy (FEFO/FIFO)
4. System suggests optimal batch
5. Confirm selection

### Expiry Reporting

The system provides:
- **Near Expiry Report**: Batches expiring in 30 days
- **Expired Batch Report**: All expired batches
- **Expiry Alert**: Automatic alerts for near-expiry batches

### Scheduled Expiry Processing

The system runs daily scheduled task to:
- Mark expired batches as inactive
- Generate near-expiry alerts
- Update batch status automatically

## Quality Control

### Creating Quality Inspection

1. Navigate to **Pharma Quality Inspection**
2. Click **New** to create inspection
3. Fill in required fields:
   - **Inspection Number**: Unique identifier
   - **Inspection Date**: Date of inspection
   - **Inspection Type**: Incoming/Outgoing/Internal
   - **Item Code**: Item being inspected
   - **Batch Number**: Batch being inspected
   - **Warehouse**: Inspection location
4. Add quality parameters:
   - Click **Add Row** in Quality Parameters table
   - Enter parameter name, specification, test method
   - Enter test result and score
   - Set weight for parameter
5. Add defects if found:
   - Click **Add Row** in Inspection Defects table
   - Enter defect type, description, severity
   - Enter quantity affected and root cause
6. System calculates overall score automatically
7. Click **Save** and **Submit**

### Quality Status Workflow

**Pending**: Batch awaiting inspection
**Approved**: Batch passed quality inspection
**Rejected**: Batch failed quality inspection
**Quarantined**: Batch placed on quality hold

### Quality Hold/Release

**Quality Hold**:
- Automatically triggered on failed inspection
- Batch cannot be used in sales
- Requires resolution before release

**Quality Release**:
- Requires corrective actions
- Must be approved by Quality Manager
- Batch becomes available for use

### Quality Reports

- **Pending Inspections**: Batches awaiting inspection
- **Failed Inspections**: Batches that failed quality checks
- **Quality Trends**: Quality performance over time

## Cold Chain Management

### Temperature Logging

1. Navigate to **Temperature Log**
2. Click **New** to create log entry
3. Fill in required fields:
   - **Log Number**: Unique identifier
   - **Log Date**: Date of reading
   - **Log Time**: Time of reading
   - **Batch Number**: Batch being monitored
   - **Temperature**: Current temperature reading
   - **Temperature Unit**: Unit of measurement (°C/°F/K)
4. Set temperature thresholds:
   - **Min Temperature**: Minimum acceptable temperature
   - **Max Temperature**: Maximum acceptable temperature
   - **Target Temperature**: Ideal temperature
5. System automatically determines temperature status:
   - **Normal**: Within acceptable range
   - **Warning**: Near threshold limits
   - **Critical**: Outside acceptable range
6. Click **Save** and **Submit**

### Temperature Excursions

When temperature exceeds thresholds:
1. System automatically creates **Temperature Excursion** record
2. Severity is determined based on deviation
3. Batch may be automatically quarantined for critical excursions
4. Alert is sent to quality team

### Managing Excursions

1. Navigate to **Temperature Excursion**
2. Open the excursion record
3. Review excursion details:
   - Temperature deviation
   - Duration of excursion
   - Affected batch
4. Set resolution:
   - Enter resolution notes
   - Select disposition (Release/Quarantine/Destroy)
   - Enter corrective actions
5. Click **Resolve** to close excursion

### Temperature Reports

- **Temperature History**: Historical temperature readings
- **Excursion Report**: All temperature excursions
- **Cold Chain Compliance**: Compliance status by batch

## Controlled Substances

### Regulatory Approval

1. Navigate to **Pharma Regulatory Approval**
2. Click **New** to create approval
3. Fill in required fields:
   - **Approval Number**: Unique identifier
   - **Batch Number**: Batch requiring approval
   - **Controlled Substance Type**: Type (Narcotic/Psychotropic/Precursor)
   - **License Number**: Regulatory license number
   - **License Expiry**: License expiry date
   - **Regulatory Authority**: Authority issuing license
4. Set approval conditions:
   - Quantity approved
   - Validity period
   - Restrictions
5. Click **Save** and **Submit**
6. Approval must be approved by authorized personnel

### Prescription Validation

For controlled substance sales:
1. Create sales invoice
2. Select controlled substance item
3. Enter **Prescription Number** (required)
4. System validates:
   - Prescription is provided
   - Regulatory approval exists
   - License is valid
   - Quantity within approved limits

### Controlled Substance Reports

- **Regulatory Approvals**: All approvals by status
- **Controlled Substance Sales**: Sales of controlled substances
- **License Expiry**: Licenses expiring soon

## Product Recall

### Initiating Recall

1. Navigate to **Pharma Product Recall**
2. Click **New** to create recall
3. Fill in required fields:
   - **Recall Number**: Unique identifier
   - **Recall Type**: Voluntary/Mandatory
   - **Recall Reason**: Reason for recall
   - **Severity**: Class I/II/III
   - **Batch Number**: Batch being recalled
4. Add affected products:
   - Click **Add Row** in Affected Products table
   - Select batch and quantity affected
5. Add affected customers:
   - Click **Add Row** in Affected Customers table
   - Select customers who received the batch
6. Click **Save** and **Submit**

### Customer Notification

1. Open the recall record
2. Click **Notify Customers** button
3. System sends notifications to all affected customers
4. Notification status is updated automatically

### Recall Resolution

1. Open the recall record
2. Enter resolution plan
3. Enter corrective actions
4. Click **Complete Recall**
5. System updates recall status to Completed

### Recall Reports

- **Open Recalls**: Active recalls
- **Recall History**: Past recalls
- **Recall Effectiveness**: Recovery rates

## Audit Trail

### Viewing Audit Logs

1. Navigate to **Audit Log**
2. Filter by:
   - Document type
   - Document name
   - User
   - Date range
   - Action type
3. View audit details:
   - Timestamp
   - User who performed action
   - Action type (Create/Update/Delete/Submit/Cancel)
   - Field changes (old and new values)
   - Change reason

### Audit Trail Reports

- **User Activity**: Actions by specific user
- **Document History**: History of specific document
- **Security Events**: Security-related events

### Audit Trail Features

- Automatic logging of all document events
- Field-level change tracking
- User activity monitoring
- Security event logging
- Export capabilities for compliance reporting

## Security Features

### Field-Level Permissions

1. Navigate to **Field Permission**
2. Click **New** to create permission
3. Fill in required fields:
   - **Permission Name**: Unique identifier
   - **DocType**: Document type
   - **Field Name**: Field to control
   - **Role**: Role to apply permission to
4. Set permissions:
   - **Read Permission**: Can view field
   - **Write Permission**: Can edit field
   - **Mask Permission**: Mask field value
   - **Hide Permission**: Hide field completely
5. Click **Save**

### Data Encryption

**Creating Encryption Key**:
1. Navigate to **Encryption Key**
2. Click **New**
3. Fill in required fields:
   - **Key Name**: Unique identifier
   - **Key Type**: Symmetric/Asymmetric
   - **Algorithm**: Encryption algorithm
   - **Key Length**: Key length in bits
4. System generates key automatically
5. Click **Save**

**Key Rotation**:
1. Open encryption key record
2. Click **Rotate Key** button
3. System generates new key
4. Old key is deactivated
5. Update encryption to use new key

### Security Best Practices

- Regularly rotate encryption keys
- Review field permissions periodically
- Monitor audit logs for suspicious activity
- Keep encryption keys secure
- Follow regulatory requirements for data protection

## Troubleshooting

### Common Issues

**Batch cannot be created**:
- Verify batch number is unique
- Check all required fields are filled
- Ensure expiry date is after manufacturing date

**Quality inspection fails**:
- Verify batch exists and is active
- Check quality parameters are valid
- Ensure overall score meets passing criteria

**Temperature excursion not created**:
- Verify temperature exceeds thresholds
- Check cold chain is enabled for batch
- Ensure temperature log is submitted

**Controlled substance sale blocked**:
- Verify regulatory approval exists
- Check license is valid
- Ensure prescription is provided if required
- Verify quantity is within approved limits

**Product recall not working**:
- Verify batch exists and is active
- Check affected customers are added
- Ensure recall is submitted

### Getting Help

For additional support:
- Contact your system administrator
- Review API documentation for technical details
- Check system logs for error details
- Contact Omnexa support at support@omnexa.com

### System Requirements

- Frappe Framework v15+
- Python 3.10+
- MySQL 8.0+
- Redis (for caching)
- Internet connection (for API calls)

### Browser Requirements

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Best Practices

### Batch Management
- Always validate batch information before submission
- Use consistent batch numbering conventions
- Regularly review batch status
- Implement proper quarantine procedures

### Quality Control
- Conduct inspections promptly upon receipt
- Document all inspection results thoroughly
- Follow up on failed inspections quickly
- Maintain quality records for compliance

### Cold Chain Management
- Log temperature readings regularly
- Monitor for temperature excursions
- Respond quickly to alerts
- Maintain proper documentation

### Regulatory Compliance
- Maintain current regulatory approvals
- Monitor license expiry dates
- Keep accurate records of controlled substances
- Follow all regulatory requirements

### Security
- Regularly review and update permissions
- Rotate encryption keys periodically
- Monitor audit logs for suspicious activity
- Follow data protection regulations
