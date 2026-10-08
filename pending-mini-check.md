production completion track before Chat Lab:
Lesson 59: Production Launch Readiness
- Run check --deploy
- Configure Render production environment variables
- Separate local, sandbox, and production credentials
- Configure custom domain and HTTPS
- Configure database backups
- Configure static/media storage
- Confirm Resend sender domain
- Set up worker/scheduler for process_jobs
- Create a final launch checklist
Lesson 60: Background Worker Deployment
- Run async jobs continuously in production
- Configure Render worker or cron job
- Monitor failed jobs
- Retry stuck jobs
- Prevent duplicate workers from processing the same job
- Test email, refund, and webhook jobs in production-like conditions
Lesson 61: Pathao Integration Completion
- Build the complete Pathao adapter
- Handle city, zone, and area IDs
- Create real sandbox shipments
- Store Pathao consignment references
- Sync tracking statuses
- Process Pathao webhooks
- Add retry and failure handling
Because the Pathao sandbox currently returns 522, we can still complete the adapter using mocked provider responses and contract tests. Actual sandbox verification will happen when their API becomes reachable.
Lesson 62: bKash Payment Integration
- Create bKash payment session
- Redirect/customer payment flow
- Execute and verify payment
- Store transaction IDs
- Handle cancellation and failure
- Implement bKash webhook/callback verification
- Prevent duplicate payment processing
- Add sandbox tests
Lesson 63: Real-World Business Readiness
- Shipping and return policies
- Privacy policy and terms
- Tax and invoice considerations
- Customer support workflow
- Product availability rules
- Refund timeframes
- Order notification emails
- Backup and recovery procedure
Lesson 64: Final Production Simulation
Run the entire flow using production-like configuration:
Customer visits site
-> creates account
-> adds product
-> checks out
-> pays with sandbox provider
-> webhook arrives
-> inventory decreases
-> receipt job runs
-> shipment is created
-> tracking updates
-> order is delivered
-> return is requested
-> refund is issued
After that, the checkout app would be ready for a controlled real-world launch.
Then we move to:
Chat Lab
So the revised path is:
59 Production launch
60 Worker deployment
61 Pathao
62 bKash
63 Business readiness
64 Full production simulation
-> Chat Lab
The important distinction is that Lessons 59–60 are needed for almost any launch, while Lessons 61–62 are provider-specific. The architecture is already ready for them; we just need to connect and verify each provider properly.