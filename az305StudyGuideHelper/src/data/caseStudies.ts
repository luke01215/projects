import { CaseStudy } from '../types/caseStudy';

export const caseStudies: CaseStudy[] = [
  {
    id: 'cs1',
    title: 'Contoso Manufacturing - Global E-Commerce Migration',
    scenario: {
      company: 'Contoso Manufacturing',
      industry: 'Manufacturing & E-Commerce',
      currentState: [
        'On-premises data center in Chicago with 200 VMs running Windows Server 2016 and SQL Server 2017',
        'E-commerce website receives 10,000 requests/day (peaks at 50,000 during sales)',
        'MySQL database for product catalog (2TB), SQL Server for orders (500GB)',
        'Users across North America, Europe, and Asia Pacific',
        'Current RTO: 24 hours, RPO: 4 hours',
        'Compliance: Must retain data for 7 years, PCI-DSS required for payment data'
      ],
      requirements: [
        'Migrate to Azure with minimal downtime',
        'Improve global user experience (target <200ms latency)',
        'Reduce RTO to 4 hours, RPO to 1 hour',
        'Auto-scale during traffic spikes',
        'Implement DevOps CI/CD pipeline',
        'Secure payment processing',
        'Cost optimization - reduce infrastructure costs by 30%'
      ],
      constraints: [
        'Budget: $50,000/month for Azure services',
        'Migration timeline: 6 months',
        'Must maintain PCI-DSS compliance',
        'Some legacy applications cannot be refactored',
        'Development team familiar with .NET and Node.js'
      ]
    },
    questions: [
      {
        id: 'cs1q1',
        question: 'What Azure service should you recommend for the e-commerce web application to meet global latency requirements?',
        options: [
          'Azure App Service in a single region with Azure CDN',
          'Azure Front Door with Azure App Service in multiple regions',
          'Azure Traffic Manager with App Service in multiple regions',
          'Azure Application Gateway with VM Scale Sets'
        ],
        correctAnswer: 1,
        explanation: 'Azure Front Door provides global Layer 7 load balancing with intelligent routing, SSL offload, and uses Microsoft\'s global edge network for <200ms latency. It can route to App Service instances in multiple regions and provides instant failover. Traffic Manager is DNS-based (slower), and CDN alone doesn\'t provide application-level routing.',
        topic: 'Infrastructure - Global Distribution'
      },
      {
        id: 'cs1q2',
        question: 'How should you migrate the SQL Server databases to meet RTO/RPO requirements while minimizing costs?',
        options: [
          'Azure SQL Database with active geo-replication',
          'SQL Server on Azure VMs with Always On Availability Groups',
          'Azure SQL Managed Instance with auto-failover groups',
          'Azure SQL Database in a single region with geo-redundant backup'
        ],
        correctAnswer: 2,
        explanation: 'Azure SQL Managed Instance provides near 100% SQL Server compatibility for lift-and-shift, and auto-failover groups provide <1 hour RTO and RPO. It\'s more cost-effective than VMs (no OS management) while supporting instance-level features. Single region doesn\'t meet HA requirements, and SQL Database may require code changes.',
        topic: 'Data Storage - High Availability'
      },
      {
        id: 'cs1q3',
        question: 'What storage solution should you use for the 7-year data retention requirement to minimize costs?',
        options: [
          'Azure Blob Storage Hot tier with lifecycle management',
          'Azure Blob Storage with lifecycle policies moving to Archive tier after 90 days',
          'Azure SQL Database with long-term retention',
          'Azure Data Lake Storage Gen2 Cool tier'
        ],
        correctAnswer: 1,
        explanation: 'Blob Storage with lifecycle management can automatically transition data to Archive tier (lowest cost) after 90 days. Archive tier is perfect for compliance data that\'s rarely accessed. Hot tier would be too expensive for 7 years. SQL Database LTR is for backups, not general data. Cool tier is more expensive than Archive for long-term retention.',
        topic: 'Data Storage - Cost Optimization'
      },
      {
        id: 'cs1q4',
        question: 'How should you secure payment processing to maintain PCI-DSS compliance?',
        options: [
          'Store payment data encrypted in Azure SQL Database',
          'Use Azure Payment HSM with tokenization and store tokens only',
          'Use Azure Key Vault to encrypt payment data at rest',
          'Implement client-side encryption before sending to Azure'
        ],
        correctAnswer: 1,
        explanation: 'Azure Payment HSM provides PCI-DSS compliant hardware security modules for payment processing. Best practice is tokenization - never store actual payment data, only tokens. This removes most Azure resources from PCI-DSS scope. Simply encrypting payment data in SQL still requires the entire database to be PCI-DSS compliant.',
        topic: 'Security - Compliance'
      },
      {
        id: 'cs1q5',
        question: 'What should you use for the CI/CD pipeline to deploy the .NET and Node.js applications?',
        options: [
          'Azure DevOps with Azure Pipelines deploying to App Service deployment slots',
          'GitHub Actions deploying directly to production App Service',
          'Azure Automation with runbooks',
          'Jenkins on Azure VMs with manual deployment'
        ],
        correctAnswer: 0,
        explanation: 'Azure DevOps Pipelines provides native support for .NET and Node.js, integrates with App Service deployment slots for blue-green deployments (zero downtime), and includes testing/approval gates. Deploying directly to production is risky. Automation runbooks aren\'t designed for application deployment. Jenkins on VMs adds management overhead.',
        topic: 'Infrastructure - DevOps'
      }
    ]
  },
  {
    id: 'cs2',
    title: 'Fabrikam Healthcare - HIPAA Compliant Patient Portal',
    scenario: {
      company: 'Fabrikam Healthcare',
      industry: 'Healthcare',
      currentState: [
        'Patient portal accessed by 500,000 patients and 5,000 medical staff',
        'On-premises SQL Server database with patient records (10TB)',
        'DICOM medical imaging files stored on file servers (50TB)',
        'Integration with 3rd-party lab systems via SOAP web services',
        'Mobile app for patients (iOS and Android)',
        'Peak usage: 8am-6pm EST weekdays'
      ],
      requirements: [
        'HIPAA compliance mandatory',
        'Encrypt all data at rest and in transit',
        'Audit all access to patient data',
        'Implement just-in-time admin access',
        'Multi-factor authentication for all users',
        'Disaster recovery in different geography',
        'Support telehealth video calls (added during COVID)',
        '99.9% availability SLA'
      ],
      constraints: [
        'Cannot use public endpoints for databases',
        'Medical staff must access via hospital network or VPN',
        'PHI (Protected Health Information) cannot leave US',
        'Budget constraints - prefer PaaS over IaaS',
        'Must maintain change logs for 10 years'
      ]
    },
    questions: [
      {
        id: 'cs2q1',
        question: 'What database solution should you recommend for the patient records?',
        options: [
          'Azure SQL Database with public endpoint disabled',
          'Azure SQL Managed Instance with private endpoint',
          'Azure Cosmos DB with private endpoint',
          'SQL Server on Azure VMs in a VNet'
        ],
        correctAnswer: 1,
        explanation: 'Azure SQL Managed Instance with private endpoint meets all requirements: PaaS (lower management), no public endpoints (security), VNet integration for hospital network access, supports geo-replication for DR, HIPAA compliant, and provides audit logging. SQL Database lacks some enterprise features. VMs have higher management overhead.',
        topic: 'Data Storage - Security'
      },
      {
        id: 'cs2q2',
        question: 'How should you store and manage the 50TB of DICOM medical imaging files?',
        options: [
          'Azure Blob Storage Hot tier with Azure CDN',
          'Azure Blob Storage Cool tier with private endpoints and immutability policies',
          'Azure Files Premium with SMB access',
          'Azure NetApp Files with snapshots'
        ],
        correctAnswer: 1,
        explanation: 'Blob Storage Cool tier is cost-effective for infrequently accessed files. Private endpoints keep traffic off public internet (HIPAA requirement). Immutability policies prevent tampering and support 10-year retention for compliance. Hot tier is too expensive for archival data. Azure Files and NetApp Files are more expensive for this use case.',
        topic: 'Data Storage - Compliance'
      },
      {
        id: 'cs2q3',
        question: 'What should you implement for just-in-time admin access to meet HIPAA audit requirements?',
        options: [
          'Azure AD Privileged Identity Management (PIM) with approval workflow and audit logs',
          'Create temporary admin accounts that expire after 8 hours',
          'Use Azure AD Conditional Access with MFA',
          'Implement Azure RBAC with custom roles'
        ],
        correctAnswer: 0,
        explanation: 'PIM provides just-in-time privileged access with time-bound permissions, approval workflows, and comprehensive audit logs (required for HIPAA). It automatically removes access after the time period. Temporary accounts require manual management. Conditional Access doesn\'t provide JIT access. RBAC alone doesn\'t provide time-bound access.',
        topic: 'Identity - Governance'
      },
      {
        id: 'cs2q4',
        question: 'How should you ensure PHI data stays within the United States?',
        options: [
          'Deploy all resources in US regions and use Azure Policy to prevent creation outside US',
          'Use resource locks on all resources',
          'Implement Network Security Groups to block traffic to non-US regions',
          'Use Azure Firewall to filter outbound traffic'
        ],
        correctAnswer: 0,
        explanation: 'Azure Policy with location restrictions (deny effect) prevents resources from being created outside allowed US regions, enforcing data residency. This is the governance approach. Resource locks prevent deletion/modification but not location. NSGs and Firewall control network traffic, not data residency.',
        topic: 'Governance - Compliance'
      },
      {
        id: 'cs2q5',
        question: 'What solution should you use for telehealth video calls with 99.9% availability?',
        options: [
          'Azure Communication Services with Azure Media Services',
          'Third-party video service integrated via API Management',
          'Custom WebRTC solution on Azure VMs',
          'Azure Virtual Desktop for screen sharing'
        ],
        correctAnswer: 0,
        explanation: 'Azure Communication Services provides HIPAA-compliant video/voice calling with 99.9% SLA, built-in encryption, and Azure Media Services for recording (if needed). It\'s a managed service (PaaS). Third-party services may not be HIPAA compliant. Custom WebRTC requires management. AVD is for desktop virtualization, not video calls.',
        topic: 'Infrastructure - Communication'
      },
      {
        id: 'cs2q6',
        question: 'How should you implement disaster recovery to meet the different geography requirement?',
        options: [
          'Azure Site Recovery replicating to a paired region',
          'Azure Backup with geo-redundant storage',
          'Manual failover to secondary region with Azure Traffic Manager',
          'SQL Managed Instance auto-failover group to different US geography'
        ],
        correctAnswer: 3,
        explanation: 'SQL Managed Instance auto-failover groups provide automatic replication and failover to a different geography (e.g., East US to West US), meeting DR requirements. ASR is for VMs (we\'re using PaaS). Azure Backup alone doesn\'t provide active failover. Manual failover doesn\'t meet availability requirements.',
        topic: 'Business Continuity - DR'
      }
    ]
  },
  {
    id: 'cs3',
    title: 'Tailwind Traders - Hybrid Cloud Infrastructure',
    scenario: {
      company: 'Tailwind Traders',
      industry: 'Retail',
      currentState: [
        '1,200 retail stores across North America with local servers',
        'Corporate data center in Dallas with Active Directory, file servers, and legacy apps',
        'Point-of-sale (POS) systems in stores need <5ms latency',
        'Inventory management system (cannot be refactored) requires SQL Server with cross-database queries',
        'Black Friday traffic is 50x normal load',
        '500 office workers need access to file shares and internal apps'
      ],
      requirements: [
        'Migrate to hybrid cloud while keeping critical systems on-premises',
        'Centralized identity management across on-prem and cloud',
        'Low-latency processing for POS transactions',
        'Auto-scale web applications during peak periods',
        'Secure connectivity between stores, corporate, and Azure',
        'Backup and DR for all systems',
        'Support for future IoT sensors in stores'
      ],
      constraints: [
        'Cannot replace POS hardware (5-year contracts)',
        'Must maintain existing Active Directory domain',
        'Limited IT staff at retail locations',
        'Some applications require direct file server access (SMB)',
        'Network bandwidth at stores: 100 Mbps'
      ]
    },
    questions: [
      {
        id: 'cs3q1',
        question: 'What hybrid identity solution should you implement?',
        options: [
          'Azure AD with Password Hash Sync',
          'Azure AD with Pass-through Authentication and Seamless SSO',
          'Azure AD Domain Services',
          'Federation with AD FS'
        ],
        correctAnswer: 1,
        explanation: 'Pass-through Authentication keeps password validation on-premises (security), Seamless SSO provides transparent authentication for cloud apps, and it maintains the existing AD domain. Password Hash Sync syncs hashes to cloud (security concern). AD DS creates a managed domain (unnecessary). AD FS adds complexity and infrastructure.',
        topic: 'Identity - Hybrid'
      },
      {
        id: 'cs3q2',
        question: 'How should you handle the low-latency requirement for POS transactions?',
        options: [
          'Deploy Azure Stack HCI in each store',
          'Use Azure IoT Edge devices with local processing',
          'Deploy VMs in the nearest Azure region',
          'Use Azure Cache for Redis in each region'
        ],
        correctAnswer: 1,
        explanation: 'Azure IoT Edge enables local processing at the edge (in-store) with <5ms latency, even without internet connectivity. It syncs data to cloud when available. Stack HCI is expensive for 1,200 stores. Azure VMs in regions still have network latency (>5ms). Redis is for caching, not transaction processing.',
        topic: 'Infrastructure - Edge Computing'
      },
      {
        id: 'cs3q3',
        question: 'What connectivity solution should you use between stores, corporate datacenter, and Azure?',
        options: [
          'Site-to-Site VPN from each store to Azure',
          'Azure Virtual WAN with SD-WAN integration',
          'ExpressRoute with Global Reach',
          'Point-to-Site VPN for each location'
        ],
        correctAnswer: 1,
        explanation: 'Azure Virtual WAN with SD-WAN provides hub-spoke topology, optimized routing between stores/corporate/Azure, and easy management at scale (1,200+ sites). S2S VPN from each store is management nightmare. ExpressRoute is too expensive for retail stores. P2S is for individual users, not sites.',
        topic: 'Infrastructure - Hybrid Networking'
      },
      {
        id: 'cs3q4',
        question: 'Where should you migrate the inventory management system that requires cross-database queries?',
        options: [
          'Azure SQL Database elastic pool',
          'Azure SQL Managed Instance',
          'Azure Cosmos DB',
          'Azure Synapse Analytics dedicated SQL pool'
        ],
        correctAnswer: 1,
        explanation: 'SQL Managed Instance supports cross-database queries (legacy app requirement), provides near 100% SQL Server compatibility, and is PaaS (less management). SQL Database doesn\'t support cross-database queries. Cosmos DB is NoSQL (incompatible). Synapse is for analytics, not transactional workloads.',
        topic: 'Data Storage - Migration'
      },
      {
        id: 'cs3q5',
        question: 'How should you handle file server access for office workers while meeting SMB requirement?',
        options: [
          'Azure Files with Azure AD authentication',
          'Azure Files with hybrid identity and Azure File Sync',
          'Azure NetApp Files',
          'File servers on Azure VMs'
        ],
        correctAnswer: 1,
        explanation: 'Azure Files with hybrid identity supports SMB access using existing AD credentials. Azure File Sync keeps a cache on-premises for frequently accessed files (performance) while tiering older files to cloud (cost savings). Pure Azure Files works but File Sync adds performance. NetApp is more expensive. VMs require more management.',
        topic: 'Data Storage - Hybrid'
      },
      {
        id: 'cs3q6',
        question: 'What solution should you use to auto-scale web applications during Black Friday (50x traffic)?',
        options: [
          'Azure VM Scale Sets with scheduled scaling',
          'Azure App Service with autoscale rules based on CPU and HTTP queue length',
          'Azure Kubernetes Service with horizontal pod autoscaler',
          'Pre-provision 50x capacity and scale down after'
        ],
        correctAnswer: 1,
        explanation: 'App Service autoscale with multiple metrics (CPU and HTTP queue) provides fast, automatic scaling for web apps. It\'s PaaS (less management) and cost-effective (pay for what you use). VMSS requires more management. AKS is overkill for web apps. Pre-provisioning wastes money 364 days/year.',
        topic: 'Infrastructure - Auto-scaling'
      }
    ]
  }
];
