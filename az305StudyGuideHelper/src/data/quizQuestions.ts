import { QuizQuestion } from '../types';

export const quizQuestions: QuizQuestion[] = [
  {
    id: 'q1',
    domain: 'Identity, Governance, and Monitoring',
    question: 'You need to ensure that users can request just-in-time access to Azure resources. Which Azure AD feature should you use?',
    options: [
      'Azure AD Conditional Access',
      'Azure AD Privileged Identity Management (PIM)',
      'Azure AD Identity Protection',
      'Azure RBAC'
    ],
    correctAnswer: 1,
    explanation: 'Azure AD PIM enables just-in-time privileged access with time-bound permissions, approval workflows, and access reviews.',
    difficulty: 'easy'
  },
  {
    id: 'q2',
    domain: 'Data Storage',
    question: 'Your company stores frequently accessed data and data that is rarely accessed. You need to minimize storage costs. Which solution should you recommend?',
    options: [
      'Store all data in Hot tier',
      'Use lifecycle management to move data to Cool/Archive tiers',
      'Use premium SSD for all storage',
      'Implement Azure NetApp Files'
    ],
    correctAnswer: 1,
    explanation: 'Azure Blob Storage lifecycle management policies can automatically transition blobs to Cool or Archive tiers based on last modification time, optimizing costs.',
    difficulty: 'medium'
  },
  {
    id: 'q3',
    domain: 'Business Continuity',
    question: 'You need to replicate Azure VMs to another region for disaster recovery with minimal RTO. What should you use?',
    options: [
      'Azure Backup',
      'Azure Site Recovery',
      'Geo-redundant storage',
      'Availability Sets'
    ],
    correctAnswer: 1,
    explanation: 'Azure Site Recovery provides VM replication to secondary regions with orchestrated failover, meeting low RTO requirements for disaster recovery.',
    difficulty: 'easy'
  },
  {
    id: 'q4',
    domain: 'Infrastructure',
    question: 'You need to provide SSL termination, URL-based routing, and Web Application Firewall capabilities. Which service should you deploy?',
    options: [
      'Azure Load Balancer',
      'Azure Traffic Manager',
      'Azure Application Gateway',
      'Network Security Group'
    ],
    correctAnswer: 2,
    explanation: 'Azure Application Gateway is a Layer 7 load balancer that provides SSL termination, URL-based routing, and optional WAF capabilities.',
    difficulty: 'medium'
  },
  {
    id: 'q5',
    domain: 'Identity, Governance, and Monitoring',
    question: 'You need to enforce that all storage accounts must use HTTPS. Which Azure service should you use?',
    options: [
      'Azure Monitor',
      'Azure Security Center',
      'Azure Policy',
      'Azure Blueprints'
    ],
    correctAnswer: 2,
    explanation: 'Azure Policy can enforce compliance requirements like requiring HTTPS for storage accounts using a deny or audit effect.',
    difficulty: 'easy'
  },
  {
    id: 'q6',
    domain: 'Data Storage',
    question: 'You need a globally distributed database with <10ms latency and support for multiple consistency models. What should you use?',
    options: [
      'Azure SQL Database with geo-replication',
      'Azure Cosmos DB',
      'Azure Database for PostgreSQL',
      'Azure Synapse Analytics'
    ],
    correctAnswer: 1,
    explanation: 'Azure Cosmos DB provides global distribution, guaranteed <10ms latency, and five consistency models (strong, bounded staleness, session, consistent prefix, eventual).',
    difficulty: 'easy'
  },
  {
    id: 'q7',
    domain: 'Infrastructure',
    question: 'You need to connect to Azure VMs via RDP without exposing them to the internet. What is the most secure solution?',
    options: [
      'Assign public IPs and use NSG rules',
      'Use Azure Bastion',
      'Create a VPN connection',
      'Use Azure Firewall'
    ],
    correctAnswer: 1,
    explanation: 'Azure Bastion provides secure RDP/SSH connectivity through Azure Portal over SSL without requiring public IPs on VMs.',
    difficulty: 'medium'
  },
  {
    id: 'q8',
    domain: 'Business Continuity',
    question: 'You deploy VMs in an Availability Zone. What SLA does Microsoft provide?',
    options: [
      '99.9%',
      '99.95%',
      '99.99%',
      '99.999%'
    ],
    correctAnswer: 2,
    explanation: 'VMs deployed across Availability Zones receive a 99.99% uptime SLA, compared to 99.9% for a single VM with premium SSD.',
    difficulty: 'easy'
  },
  {
    id: 'q9',
    domain: 'Infrastructure',
    question: 'You need to filter traffic between subnets in a VNet. What should you use?',
    options: [
      'Azure Firewall',
      'Network Security Groups (NSGs)',
      'Application Security Groups (ASGs)',
      'Azure DDoS Protection'
    ],
    correctAnswer: 1,
    explanation: 'NSGs can be associated with subnets to filter inbound and outbound traffic between subnets using security rules.',
    difficulty: 'easy'
  },
  {
    id: 'q10',
    domain: 'Data Storage',
    question: 'You need 99.99% availability for storage with protection against datacenter failures in a single region. Which redundancy option should you choose?',
    options: [
      'Locally Redundant Storage (LRS)',
      'Zone Redundant Storage (ZRS)',
      'Geo Redundant Storage (GRS)',
      'Geo-Zone Redundant Storage (GZRS)'
    ],
    correctAnswer: 1,
    explanation: 'ZRS replicates data across three availability zones in a region, providing 99.99% availability and protection against datacenter-level failures.',
    difficulty: 'medium'
  },
  {
    id: 'q11',
    domain: 'Identity, Governance, and Monitoring',
    question: 'You need to query and analyze log data from multiple Azure resources using KQL. What should you use?',
    options: [
      'Azure Monitor Metrics',
      'Azure Monitor Log Analytics',
      'Azure Application Insights',
      'Azure Activity Log'
    ],
    correctAnswer: 1,
    explanation: 'Azure Monitor Log Analytics workspace allows you to run KQL queries against log data collected from multiple sources.',
    difficulty: 'easy'
  },
  {
    id: 'q12',
    domain: 'Infrastructure',
    question: 'You need to provide private connectivity to Azure PaaS services without exposing traffic to the internet. What should you implement?',
    options: [
      'Service Endpoints',
      'Azure Private Link',
      'VNet peering',
      'Site-to-Site VPN'
    ],
    correctAnswer: 1,
    explanation: 'Azure Private Link provides private connectivity to PaaS services over a private endpoint in your VNet, keeping traffic on Microsoft network.',
    difficulty: 'medium'
  },
  {
    id: 'q13',
    domain: 'Business Continuity',
    question: 'What is the minimum number of availability zones in an Azure region that supports them?',
    options: [
      '2',
      '3',
      '4',
      '5'
    ],
    correctAnswer: 1,
    explanation: 'Azure regions that support availability zones have a minimum of three physically separate zones, each with independent infrastructure.',
    difficulty: 'easy'
  },
  {
    id: 'q14',
    domain: 'Infrastructure',
    question: 'You need global HTTP load balancing with instant failover and SSL offloading. Which service should you use?',
    options: [
      'Azure Application Gateway',
      'Azure Traffic Manager',
      'Azure Front Door',
      'Azure Load Balancer'
    ],
    correctAnswer: 2,
    explanation: 'Azure Front Door provides global Layer 7 load balancing, instant failover, SSL offloading, and uses Microsoft\'s global edge network.',
    difficulty: 'medium'
  },
  {
    id: 'q15',
    domain: 'Data Storage',
    question: 'You need to migrate an on-premises SQL Server with instance-level features to Azure. What should you recommend?',
    options: [
      'Azure SQL Database',
      'Azure SQL Managed Instance',
      'SQL Server on Azure VMs',
      'Azure Database for MySQL'
    ],
    correctAnswer: 1,
    explanation: 'Azure SQL Managed Instance provides near 100% compatibility with SQL Server, including instance-level features like SQL Agent and cross-database queries.',
    difficulty: 'medium'
  },
  {
    id: 'q16',
    domain: 'Identity, Governance, and Monitoring',
    question: 'You need to organize governance across 50 Azure subscriptions. What should you implement?',
    options: [
      'Resource Groups',
      'Management Groups',
      'Azure Blueprints',
      'Azure Policy only'
    ],
    correctAnswer: 1,
    explanation: 'Management Groups provide a hierarchy to efficiently manage access, policies, and compliance across multiple subscriptions.',
    difficulty: 'easy'
  },
  {
    id: 'q17',
    domain: 'Infrastructure',
    question: 'You need dedicated private connectivity between on-premises and Azure that doesn\'t traverse the internet. What should you use?',
    options: [
      'Site-to-Site VPN',
      'Point-to-Site VPN',
      'Azure ExpressRoute',
      'Azure Virtual WAN'
    ],
    correctAnswer: 2,
    explanation: 'Azure ExpressRoute creates private connections between Azure and on-premises infrastructure through a connectivity provider, not over public internet.',
    difficulty: 'easy'
  },
  {
    id: 'q18',
    domain: 'Business Continuity',
    question: 'You need to back up Azure VMs with a managed service that handles storage and retention. What should you use?',
    options: [
      'Azure Site Recovery',
      'Managed Snapshots',
      'Azure Backup',
      'Azure Storage redundancy'
    ],
    correctAnswer: 2,
    explanation: 'Azure Backup is a managed backup service that automatically handles storage management, encryption, and retention for Azure VMs and other resources.',
    difficulty: 'easy'
  },
  {
    id: 'q19',
    domain: 'Infrastructure',
    question: 'You need to automatically scale a group of VMs based on CPU metrics. What should you deploy?',
    options: [
      'Availability Set',
      'Virtual Machine Scale Set',
      'Azure Kubernetes Service',
      'Azure Container Instances'
    ],
    correctAnswer: 1,
    explanation: 'Virtual Machine Scale Sets can automatically increase or decrease the number of VM instances based on metrics like CPU or custom metrics.',
    difficulty: 'easy'
  },
  {
    id: 'q20',
    domain: 'Data Storage',
    question: 'You need storage for big data analytics with hierarchical namespace and Hadoop compatibility. What should you use?',
    options: [
      'Azure Blob Storage (standard)',
      'Azure Data Lake Storage Gen2',
      'Azure Files',
      'Azure NetApp Files'
    ],
    correctAnswer: 1,
    explanation: 'Azure Data Lake Storage Gen2 combines Blob Storage with hierarchical namespace, optimized for big data analytics and Hadoop compatibility.',
    difficulty: 'medium'
  }
];
