# Quick Start Guide - AWS Deployment

## 🎯 Your Mission
Deploy the Electronic Inventory System to AWS using 5 services.

---

## 📋 Checklist

### Phase 1: AWS Account Setup (30 minutes)
- [ ] Create AWS account
- [ ] Add payment method
- [ ] Verify email and phone

### Phase 2: Create AWS Resources (45 minutes)
- [ ] Create S3 bucket for images
- [ ] Create RDS PostgreSQL database
- [ ] Verify email in SES
- [ ] Create IAM user with access keys
- [ ] Launch EC2 instance

### Phase 3: Deploy Application (60 minutes)
- [ ] Connect to EC2 via SSH
- [ ] Upload project files
- [ ] Install dependencies
- [ ] Configure .env file
- [ ] Run database migrations
- [ ] Start Gunicorn and Nginx

### Phase 4: Test Everything (30 minutes)
- [ ] Access website
- [ ] Upload image (S3)
- [ ] Send test email (SES)
- [ ] Check CloudWatch logs
- [ ] Test low stock alerts

**Total Time: ~2.5 hours**

---

## 📚 Documentation Files

| File | Purpose | When to Use |
|------|---------|-------------|
| **AWS_SETUP_GUIDE.md** | Create AWS account and resources | Start here - Complete first |
| **DEPLOYMENT_GUIDE.md** | Deploy application to EC2 | After AWS resources created |
| **AWS_SERVICES_DOCUMENTATION.md** | Understand how services work | Reference and troubleshooting |
| **.env.example** | Environment variables template | Configure credentials |

---

## 🚀 Quick Steps

### Step 1: Create AWS Account
```
1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Follow the signup process
4. Wait for account activation (5-15 minutes)
```

### Step 2: Create AWS Resources
Follow **AWS_SETUP_GUIDE.md** to create:
- S3 Bucket
- RDS Database
- SES Email
- IAM User
- EC2 Instance

**Save all credentials!** You'll need them for deployment.

### Step 3: Deploy to EC2
Follow **DEPLOYMENT_GUIDE.md** to:
- Connect to EC2
- Upload code
- Install dependencies
- Configure environment
- Start services

### Step 4: Access Your Application
```
http://YOUR-EC2-PUBLIC-IP/
```

---

## 💰 Costs

- **Free Tier (12 months)**: $0 - $5/month
- **After Free Tier**: ~$25-30/month

All services have free tier limits!

---

## 🆘 Need Help?

### Issue: Can't connect to EC2
- Check security group allows SSH (port 22)
- Verify .pem key permissions
- Use correct username: `ubuntu@`

### Issue: Database connection fails
- Check RDS security group
- Verify RDS endpoint in .env
- Test with psql command

### Issue: Images won't upload
- Check S3 bucket permissions
- Verify AWS credentials in .env
- Check CloudWatch logs

### Issue: Emails not sending
- Verify email in SES
- Check SES sandbox mode
- Verify SMTP credentials

---

## 📞 Support Resources

- AWS Documentation: https://docs.aws.amazon.com/
- Django Documentation: https://docs.djangoproject.com/
- Project Documentation: See README.md

---

## ✨ What You'll Have When Done

✅ Professional inventory system
✅ Running on AWS cloud
✅ Automatic email alerts
✅ Image storage in S3
✅ Managed database (RDS)
✅ Application monitoring
✅ Scalable architecture
✅ Production-ready setup

**Good luck with your deployment! 🎉**
