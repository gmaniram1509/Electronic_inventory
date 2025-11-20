# AWS Setup Guide - Electronic Inventory System

## Overview
This guide will help you deploy the Electronic Inventory Management System to AWS using 5 core services.

## AWS Services Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                             │
│                                                              │
│  ┌────────────┐      ┌──────────────┐      ┌─────────────┐ │
│  │   EC2      │─────▶│     RDS      │      │     S3      │ │
│  │  Django    │      │  PostgreSQL  │      │   Storage   │ │
│  │   App      │      │   Database   │      │  Images +   │ │
│  └────────────┘      └──────────────┘      │   Static    │ │
│       │                                     └─────────────┘ │
│       │                                                      │
│       ├─────────────────────────────────────────────────────┤
│       │                                                      │
│       ▼                        ▼                             │
│  ┌────────────┐          ┌──────────────┐                  │
│  │    SES     │          │  CloudWatch  │                  │
│  │   Email    │          │  Monitoring  │                  │
│  │  Alerts    │          │  & Logs      │                  │
│  └────────────┘          └──────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### Services Breakdown:

1. **EC2** - Runs the Django application (web server)
2. **RDS** - PostgreSQL database for inventory data
3. **S3** - Stores product images, datasheets, and static files
4. **SES** - Sends email notifications (low stock alerts)
5. **CloudWatch** - Application monitoring, logs, and metrics

---

## Prerequisites

- Credit/Debit card for AWS account verification
- Email address
- Phone number

---

## Part 1: Create AWS Account

### Step 1: Sign Up for AWS
1. Go to https://aws.amazon.com/
2. Click **"Create an AWS Account"** (top right)
3. Enter your email address
4. Choose **"Root user"**
5. Enter account name (e.g., "Electronic-Inventory-Project")
6. Click **"Verify email address"**
7. Check your email for verification code
8. Enter the verification code

### Step 2: Contact Information
1. Select **"Personal"** account type
2. Fill in your details:
   - Full Name
   - Phone Number
   - Country/Region
   - Address
3. Read and accept AWS Customer Agreement
4. Click **"Continue"**

### Step 3: Payment Information
1. Enter credit/debit card details
2. AWS will charge $1 for verification (refunded)
3. Click **"Verify and Continue"**

### Step 4: Identity Verification
1. Enter phone number
2. Choose verification method (SMS or Voice call)
3. Enter the verification code you receive
4. Click **"Continue"**

### Step 5: Choose Support Plan
1. Select **"Basic support - Free"**
2. Click **"Complete sign up"**

### Step 6: Wait for Activation
- Wait 5-15 minutes for account activation
- You'll receive a confirmation email
- Once activated, click **"Go to AWS Management Console"**

---

## Part 2: Set Up AWS Services

### Service 1: Create S3 Bucket (Storage)

**Purpose**: Store product images and static files

1. **Login to AWS Console**: https://console.aws.amazon.com/
2. Search for **"S3"** in the search bar
3. Click **"Create bucket"**
4. **Bucket Configuration**:
   - **Bucket name**: `electronic-inventory-storage` (must be globally unique)
   - **AWS Region**: Choose closest to you (e.g., `us-east-1`)
   - **Object Ownership**: ACLs disabled
   - **Block Public Access**: UNCHECK "Block all public access"
   - Check the warning acknowledgment
5. Click **"Create bucket"**

6. **Configure Bucket Policy**:
   - Click on your bucket name
   - Go to **"Permissions"** tab
   - Scroll to **"Bucket policy"**
   - Click **"Edit"**
   - Paste this policy (replace `YOUR-BUCKET-NAME` with your bucket name):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

7. Click **"Save changes"**

8. **Enable CORS**:
   - Go to **"Permissions"** tab
   - Scroll to **"Cross-origin resource sharing (CORS)"**
   - Click **"Edit"**
   - Paste:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

9. Click **"Save changes"**

**✅ S3 Setup Complete**

---

### Service 2: Create RDS Database (PostgreSQL)

**Purpose**: Store inventory data in a managed database

1. Search for **"RDS"** in AWS Console
2. Click **"Create database"**
3. **Database Configuration**:
   - **Choose a database creation method**: Standard create
   - **Engine type**: PostgreSQL
   - **Engine Version**: PostgreSQL 15.x (latest)
   - **Templates**: **Free tier** (if eligible)

4. **Settings**:
   - **DB instance identifier**: `inventory-db`
   - **Master username**: `postgres`
   - **Master password**: Choose a strong password (save it!)
   - **Confirm password**: Re-enter password

5. **Instance configuration**:
   - **DB instance class**: `db.t3.micro` (Free tier eligible)

6. **Storage**:
   - **Storage type**: General Purpose SSD (gp2)
   - **Allocated storage**: 20 GiB
   - Uncheck **"Enable storage autoscaling"** (to stay in free tier)

7. **Connectivity**:
   - **Compute resource**: Don't connect to an EC2 resource
   - **VPC**: Default VPC
   - **Public access**: **Yes** (so we can connect from EC2)
   - **VPC security group**: Create new
   - **Security group name**: `inventory-db-sg`

8. **Database authentication**: Password authentication

9. **Additional configuration**:
   - **Initial database name**: `inventorydb`
   - Uncheck **"Enable automated backups"** (to save costs)
   - Uncheck **"Enable encryption"**

10. Click **"Create database"**
11. **Wait 5-10 minutes** for database to be created
12. **Save these details**:
    - Endpoint (will appear after creation)
    - Port: 5432
    - Database name: inventorydb
    - Username: postgres
    - Password: (your password)

**✅ RDS Setup Complete**

---

### Service 3: Configure SES (Email Service)

**Purpose**: Send low stock alert emails

1. Search for **"SES"** in AWS Console
2. If prompted, click **"Get started"**
3. **Verify Email Address**:
   - Click **"Verified identities"** in left sidebar
   - Click **"Create identity"**
   - **Identity type**: Email address
   - **Email address**: Enter your email (where you want to receive alerts)
   - Click **"Create identity"**

4. **Check Your Email**:
   - You'll receive a verification email from AWS
   - Click the verification link
   - Email status should change to "Verified"

5. **Request Production Access** (Optional - for sending to any email):
   - By default, SES is in "Sandbox mode" (can only send to verified emails)
   - For production: Click "Account Dashboard" → "Request production access"
   - For testing: Just use your verified email

6. **Get SMTP Credentials**:
   - Click **"SMTP settings"** in left sidebar
   - Note the **SMTP endpoint** (e.g., `email-smtp.us-east-1.amazonaws.com`)
   - Click **"Create SMTP credentials"**
   - **IAM User Name**: `inventory-ses-smtp`
   - Click **"Create user"**
   - **IMPORTANT**: Download credentials (you can't view them again!)
   - Save:
     - SMTP Username
     - SMTP Password

**✅ SES Setup Complete**

---

### Service 4: Create IAM User (For Access Keys)

**Purpose**: Programmatic access to AWS services

1. Search for **"IAM"** in AWS Console
2. Click **"Users"** in left sidebar
3. Click **"Create user"**
4. **User details**:
   - **User name**: `inventory-app-user`
   - Click **"Next"**

5. **Set permissions**:
   - Select **"Attach policies directly"**
   - Search and select these policies:
     - `AmazonS3FullAccess`
     - `AmazonSESFullAccess`
     - `CloudWatchFullAccess`
   - Click **"Next"**

6. Review and click **"Create user"**

7. **Create Access Keys**:
   - Click on the user you just created
   - Click **"Security credentials"** tab
   - Scroll to **"Access keys"**
   - Click **"Create access key"**
   - **Use case**: Application running outside AWS
   - Click checkbox and **"Next"**
   - **Description**: "Inventory app keys"
   - Click **"Create access key"**
   - **IMPORTANT**: Download .csv file or copy:
     - Access Key ID
     - Secret Access Key
   - Click **"Done"**

**✅ IAM User Setup Complete**

---

### Service 5: CloudWatch (Automatic Setup)

**Purpose**: Monitor application logs and metrics

CloudWatch is automatically enabled! We'll configure it in the application code.

**What we'll monitor**:
- Application logs
- Database connections
- Error rates
- Low stock alerts triggered

**✅ CloudWatch Ready**

---

## Part 3: Create EC2 Instance

**Purpose**: Host the Django application

1. Search for **"EC2"** in AWS Console
2. Click **"Launch instance"**

3. **Name and tags**:
   - **Name**: `Inventory-Server`

4. **Application and OS Images**:
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Architecture**: 64-bit (x86)

5. **Instance type**:
   - **Instance type**: `t2.micro` (Free tier eligible)

6. **Key pair** (for SSH access):
   - Click **"Create new key pair"**
   - **Key pair name**: `inventory-key`
   - **Key pair type**: RSA
   - **File format**: `.pem` (for Mac/Linux) or `.ppk` (for PuTTY on Windows)
   - Click **"Create key pair"**
   - **SAVE THE FILE** - you can't download it again!

7. **Network settings**:
   - Click **"Edit"**
   - **Auto-assign public IP**: Enable
   - **Firewall (security groups)**: Create new
   - **Security group name**: `inventory-server-sg`
   - **Description**: "Security group for inventory server"
   - **Add rules**:
     - SSH (port 22) - Your IP
     - HTTP (port 80) - Anywhere (0.0.0.0/0)
     - HTTPS (port 443) - Anywhere (0.0.0.0/0)
     - Custom TCP (port 8000) - Anywhere (for Django dev server)

8. **Configure storage**:
   - **Size**: 8 GiB (default is fine)
   - **Volume type**: gp2

9. **Advanced details** (expand):
   - Leave defaults

10. **Summary**: Review everything
11. Click **"Launch instance"**
12. Wait for instance to start (1-2 minutes)
13. Click on instance ID to view details
14. **Save these details**:
    - Public IPv4 address
    - Public IPv4 DNS

**✅ EC2 Instance Created**

---

## Summary - What You Need to Save

Create a file to save all these credentials:

### S3:
- Bucket name: `electronic-inventory-storage` (or your chosen name)
- Region: (your chosen region, e.g., `us-east-1`)

### RDS:
- Endpoint: (from RDS console)
- Port: `5432`
- Database: `inventorydb`
- Username: `postgres`
- Password: (your password)

### SES:
- SMTP Endpoint: (from SES console)
- SMTP Username: (from downloaded credentials)
- SMTP Password: (from downloaded credentials)
- Verified email: (your email)

### IAM:
- Access Key ID: (from IAM user)
- Secret Access Key: (from IAM user)
- Region: (same as S3)

### EC2:
- Public IP: (from EC2 console)
- Key file: `inventory-key.pem` (downloaded file)

---

## Next Steps

Once you've completed all the AWS setup above, I will:

1. ✅ Update the Django project with AWS configurations
2. ✅ Create deployment scripts
3. ✅ Guide you through deploying to EC2
4. ✅ Set up CloudWatch monitoring
5. ✅ Test all AWS integrations

**Please complete the AWS setup steps above and let me know when you're ready to proceed with deployment!**

---

## Estimated AWS Costs

With AWS Free Tier (first 12 months):
- **EC2 t2.micro**: Free (750 hours/month)
- **RDS db.t3.micro**: Free (750 hours/month)
- **S3**: Free (5GB storage, 20,000 GET requests)
- **SES**: Free (62,000 emails/month)
- **CloudWatch**: Free (10 custom metrics, 5GB logs)

**Total: $0 - $5/month** (staying within free tier limits)

After free tier: ~$15-25/month depending on usage.

---

## Need Help?

Common issues and solutions will be added as we go through the setup together!
