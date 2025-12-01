import { Flashcard } from '../types';

export const flashcards: Flashcard[] = [
  // Domain 1: Design Identity, Governance, and Monitoring Solutions
  {
    id: 'f1',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What is Azure AD Privileged Identity Management (PIM)?',
    answer: 'PIM is a service that enables you to manage, control, and monitor access to important resources. It provides just-in-time privileged access, time-bound access, approval-based activation, and access reviews.',
    difficulty: 'medium',
    tags: ['Azure AD', 'Security', 'PIM']
  },
  {
    id: 'f2',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What are Azure Policy effects?',
    answer: 'Main effects include: Deny (blocks resource creation/update), Audit (creates warning event), Append (adds fields to resource), DeployIfNotExists (deploys resource if condition met), Modify (adds/updates/removes tags), and Disabled (policy not enforced).',
    difficulty: 'medium',
    tags: ['Azure Policy', 'Governance']
  },
  {
    id: 'f3',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What is the difference between Azure AD roles and Azure RBAC roles?',
    answer: 'Azure AD roles manage Azure AD resources (users, groups, applications). Azure RBAC roles manage Azure resources (VMs, storage, networks). They operate at different scopes and serve different purposes.',
    difficulty: 'hard',
    tags: ['Azure AD', 'RBAC', 'Security']
  },
  {
    id: 'f4',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What is Azure Monitor Log Analytics?',
    answer: 'A tool in Azure Portal to edit and run log queries against data in Azure Monitor Logs. It uses Kusto Query Language (KQL) to analyze and visualize data from multiple sources.',
    difficulty: 'easy',
    tags: ['Monitoring', 'Log Analytics', 'KQL']
  },
  {
    id: 'f5',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What are Management Groups in Azure?',
    answer: 'Containers that help manage access, policy, and compliance across multiple subscriptions. They provide organization-level governance with hierarchy up to 6 levels deep (excluding root and subscription level).',
    difficulty: 'medium',
    tags: ['Management Groups', 'Governance']
  },

  // Domain 2: Design Data Storage Solutions
  {
    id: 'f6',
    domain: 'Data Storage',
    question: 'What are the Azure Storage redundancy options?',
    answer: 'LRS (Locally Redundant), ZRS (Zone Redundant), GRS (Geo Redundant), GZRS (Geo-Zone Redundant), RA-GRS (Read-Access Geo Redundant), and RA-GZRS (Read-Access Geo-Zone Redundant). Choose based on durability, availability, and cost requirements.',
    difficulty: 'hard',
    tags: ['Storage', 'Redundancy', 'High Availability']
  },
  {
    id: 'f7',
    domain: 'Data Storage',
    question: 'When should you use Azure Blob Storage Hot, Cool, and Archive tiers?',
    answer: 'Hot: frequently accessed data. Cool: infrequently accessed data stored for at least 30 days (lower storage cost, higher access cost). Archive: rarely accessed data stored for at least 180 days (lowest storage cost, highest access cost with rehydration time).',
    difficulty: 'medium',
    tags: ['Blob Storage', 'Storage Tiers', 'Cost Optimization']
  },
  {
    id: 'f8',
    domain: 'Data Storage',
    question: 'What is Azure Cosmos DB?',
    answer: 'A globally distributed, multi-model database service with guaranteed <10ms latency, 99.999% availability SLA, automatic scaling, and multiple consistency levels. Supports SQL, MongoDB, Cassandra, Gremlin, and Table APIs.',
    difficulty: 'easy',
    tags: ['Cosmos DB', 'NoSQL', 'Global Distribution']
  },
  {
    id: 'f9',
    domain: 'Data Storage',
    question: 'What is the difference between Azure SQL Database and Azure SQL Managed Instance?',
    answer: 'SQL Database is PaaS for single/pooled databases with limited instance-level features. SQL Managed Instance provides near 100% SQL Server compatibility with instance-level features like cross-database queries, SQL Agent, and VNet integration.',
    difficulty: 'hard',
    tags: ['SQL Database', 'SQL Managed Instance', 'PaaS']
  },
  {
    id: 'f10',
    domain: 'Data Storage',
    question: 'What is Azure Data Lake Storage Gen2?',
    answer: 'A set of capabilities for big data analytics built on Azure Blob Storage. It combines hierarchical namespace, Hadoop compatibility, fine-grained access control, and low-cost tiered storage.',
    difficulty: 'medium',
    tags: ['Data Lake', 'Big Data', 'Storage']
  },

  // Domain 3: Design Business Continuity Solutions
  {
    id: 'f11',
    domain: 'Business Continuity',
    question: 'What is the difference between RTO and RPO?',
    answer: 'RTO (Recovery Time Objective): Maximum acceptable time to restore service after disruption. RPO (Recovery Point Objective): Maximum acceptable amount of data loss measured in time. RTO focuses on downtime, RPO on data loss.',
    difficulty: 'easy',
    tags: ['DR', 'RTO', 'RPO']
  },
  {
    id: 'f12',
    domain: 'Business Continuity',
    question: 'What is Azure Site Recovery?',
    answer: 'A disaster recovery service that replicates workloads from primary to secondary location. Supports VM replication, orchestrated failover/failback, replication of on-premises VMs and physical servers to Azure, and Azure-to-Azure VM replication.',
    difficulty: 'medium',
    tags: ['Site Recovery', 'DR', 'Replication']
  },
  {
    id: 'f13',
    domain: 'Business Continuity',
    question: 'What are Azure Availability Zones?',
    answer: 'Physically separate locations within an Azure region, each with independent power, cooling, and networking. They provide high availability with 99.99% VM uptime SLA when deploying across zones.',
    difficulty: 'easy',
    tags: ['Availability Zones', 'High Availability']
  },
  {
    id: 'f14',
    domain: 'Business Continuity',
    question: 'What is Azure Backup?',
    answer: 'A PaaS solution for backing up data to Azure. Supports Azure VMs, SQL/SAP databases in VMs, Azure Files, on-premises servers. Features include automatic storage management, unlimited scaling, encryption, and long-term retention.',
    difficulty: 'easy',
    tags: ['Backup', 'Data Protection']
  },
  {
    id: 'f15',
    domain: 'Business Continuity',
    question: 'What are paired regions in Azure?',
    answer: 'Each Azure region is paired with another region within the same geography (at least 300 miles apart). Benefits include sequential updates, prioritized recovery, data residency compliance, and platform updates rolled out one region at a time.',
    difficulty: 'medium',
    tags: ['Paired Regions', 'DR', 'Geography']
  },

  // Domain 4: Design Infrastructure Solutions
  {
    id: 'f16',
    domain: 'Infrastructure',
    question: 'What is Azure Virtual WAN?',
    answer: 'A networking service providing optimized and automated branch connectivity. Brings together VPN, ExpressRoute, and P2S user VPN with a single operational interface. Supports global transit architecture.',
    difficulty: 'medium',
    tags: ['Virtual WAN', 'Networking', 'Connectivity']
  },
  {
    id: 'f17',
    domain: 'Infrastructure',
    question: 'What are the differences between Azure Load Balancer and Application Gateway?',
    answer: 'Load Balancer: Layer 4 (TCP/UDP), regional, port forwarding. Application Gateway: Layer 7 (HTTP/HTTPS), regional, URL-based routing, SSL termination, WAF, session affinity, multi-site hosting.',
    difficulty: 'hard',
    tags: ['Load Balancer', 'Application Gateway', 'Networking']
  },
  {
    id: 'f18',
    domain: 'Infrastructure',
    question: 'What is Azure Front Door?',
    answer: 'A global, scalable entry point using Microsoft network edge locations. Provides Layer 7 load balancing, SSL offload, URL-based routing, session affinity, WAF, and global HTTP load balancing with instant failover.',
    difficulty: 'medium',
    tags: ['Front Door', 'CDN', 'Global Load Balancing']
  },
  {
    id: 'f19',
    domain: 'Infrastructure',
    question: 'What is Azure Kubernetes Service (AKS)?',
    answer: 'A managed Kubernetes container orchestration service. Azure handles critical tasks like health monitoring and maintenance. Features include integrated CI/CD, enterprise-grade security, auto-scaling, and built-in monitoring.',
    difficulty: 'easy',
    tags: ['AKS', 'Kubernetes', 'Containers']
  },
  {
    id: 'f20',
    domain: 'Infrastructure',
    question: 'What are Virtual Machine Scale Sets?',
    answer: 'Service to create and manage a group of load-balanced VMs. Automatically increases/decreases VM count based on demand or schedule. Provides high availability, easy application deployment, and supports up to 1000 VMs.',
    difficulty: 'easy',
    tags: ['VMSS', 'Auto-scaling', 'Compute']
  },
  {
    id: 'f21',
    domain: 'Infrastructure',
    question: 'What is Azure Private Link?',
    answer: 'Provides private connectivity from a VNet to Azure PaaS services, customer-owned services, or Microsoft partner services. Traffic stays on Microsoft network, eliminating public internet exposure. Works across subscriptions and AD tenants.',
    difficulty: 'medium',
    tags: ['Private Link', 'Networking', 'Security']
  },
  {
    id: 'f22',
    domain: 'Infrastructure',
    question: 'What is Azure Bastion?',
    answer: 'A fully managed PaaS service providing secure RDP/SSH connectivity to VMs directly through Azure Portal over SSL. Eliminates need for public IPs on VMs, protects against port scanning, and hardening against zero-day exploits.',
    difficulty: 'easy',
    tags: ['Bastion', 'Security', 'Remote Access']
  },
  {
    id: 'f23',
    domain: 'Infrastructure',
    question: 'What are Network Security Groups (NSGs)?',
    answer: 'Contain security rules that allow/deny inbound or outbound network traffic. Rules are processed by priority (100-4096). Can be associated with subnets or individual NICs. Use service tags and ASGs for simplified management.',
    difficulty: 'medium',
    tags: ['NSG', 'Security', 'Networking']
  },
  {
    id: 'f24',
    domain: 'Infrastructure',
    question: 'What is Azure ExpressRoute?',
    answer: 'Creates private connections between Azure datacenters and on-premises infrastructure. Traffic doesn\'t go over public internet. Offers faster speeds (up to 100 Gbps), lower latency, higher reliability, and supports Global Reach for cross-location connectivity.',
    difficulty: 'medium',
    tags: ['ExpressRoute', 'Hybrid', 'Networking']
  },

  // Additional Identity, Governance, and Monitoring
  {
    id: 'f25',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What is Azure Key Vault?',
    answer: 'A cloud service for securely storing and accessing secrets, keys, and certificates. Supports HSM-backed keys, access policies, certificate management, and integration with Azure services. Helps centralize application secrets and control their distribution.',
    difficulty: 'easy',
    tags: ['Key Vault', 'Security', 'Secrets Management']
  },
  {
    id: 'f26',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What are Azure AD Conditional Access policies?',
    answer: 'If-then statements that enforce access controls based on conditions like user/location/device/app/risk. Can require MFA, block access, or grant limited access. Core component of Zero Trust security model.',
    difficulty: 'medium',
    tags: ['Conditional Access', 'Azure AD', 'Zero Trust']
  },
  {
    id: 'f27',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What is the difference between Azure Monitor Metrics and Logs?',
    answer: 'Metrics: numerical time-series data, near real-time, lightweight, good for alerts. Logs: text/structured data stored in Log Analytics, queried with KQL, better for detailed analysis and troubleshooting.',
    difficulty: 'medium',
    tags: ['Azure Monitor', 'Metrics', 'Logs']
  },
  {
    id: 'f28',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What is Azure Lighthouse?',
    answer: 'Enables multi-tenant management at scale for service providers. Allows delegated resource management across customer tenants with enhanced visibility, automation, and governance. Supports cross-tenant management scenarios.',
    difficulty: 'hard',
    tags: ['Lighthouse', 'Multi-tenant', 'Governance']
  },
  {
    id: 'f29',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What are Managed Identities in Azure?',
    answer: 'Provides Azure services with an automatically managed identity in Azure AD. Two types: System-assigned (tied to resource lifecycle) and User-assigned (independent lifecycle). Eliminates need to manage credentials in code.',
    difficulty: 'medium',
    tags: ['Managed Identity', 'Azure AD', 'Security']
  },
  {
    id: 'f30',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What is Azure Resource Graph?',
    answer: 'A service that enables efficient resource exploration and querying at scale across subscriptions. Uses KQL to query resource properties, relationships, and changes. Provides inventory, compliance, and governance insights.',
    difficulty: 'medium',
    tags: ['Resource Graph', 'KQL', 'Governance']
  },

  // Additional Data Storage
  {
    id: 'f31',
    domain: 'Data Storage',
    question: 'What are the Cosmos DB consistency levels?',
    answer: 'Strong (linearizability), Bounded Staleness (configurable lag), Session (read-your-writes), Consistent Prefix (reads never see out-of-order writes), Eventual (weakest, highest performance). Trade-offs between consistency, availability, latency, and throughput.',
    difficulty: 'hard',
    tags: ['Cosmos DB', 'Consistency', 'CAP Theorem']
  },
  {
    id: 'f32',
    domain: 'Data Storage',
    question: 'What is Azure Synapse Analytics?',
    answer: 'Unified analytics service combining data integration, enterprise data warehousing, and big data analytics. Includes SQL pools (dedicated/serverless), Spark pools, Data Explorer, and integrated pipelines. Formerly SQL Data Warehouse.',
    difficulty: 'medium',
    tags: ['Synapse', 'Data Warehouse', 'Analytics']
  },
  {
    id: 'f33',
    domain: 'Data Storage',
    question: 'When should you use Azure Table Storage vs Cosmos DB Table API?',
    answer: 'Table Storage: low-cost NoSQL key-value store, simple scenarios, no global distribution. Cosmos DB Table API: need global distribution, low latency (<10ms), automatic indexing, multiple consistency models, higher throughput requirements.',
    difficulty: 'hard',
    tags: ['Table Storage', 'Cosmos DB', 'NoSQL']
  },
  {
    id: 'f34',
    domain: 'Data Storage',
    question: 'What is Azure Cache for Redis?',
    answer: 'In-memory data store based on Redis. Provides high throughput and low-latency data access. Common patterns: cache-aside, content cache, session store, job queuing, distributed transactions. Supports clustering and persistence.',
    difficulty: 'easy',
    tags: ['Redis', 'Caching', 'Performance']
  },
  {
    id: 'f35',
    domain: 'Data Storage',
    question: 'What is the difference between Azure Files and Azure Blob Storage?',
    answer: 'Azure Files: SMB/NFS file shares, lift-and-shift scenarios, shared access across VMs, supports file/directory hierarchy. Blob Storage: object storage, REST API access, optimized for streaming/random access, three blob types (block/append/page).',
    difficulty: 'medium',
    tags: ['Azure Files', 'Blob Storage', 'Storage']
  },
  {
    id: 'f36',
    domain: 'Data Storage',
    question: 'What is Azure Data Factory?',
    answer: 'Cloud-based ETL and data integration service. Creates data-driven workflows (pipelines) to orchestrate data movement and transformation. Supports 90+ connectors, mapping data flows, SSIS integration, and scheduling.',
    difficulty: 'easy',
    tags: ['Data Factory', 'ETL', 'Data Integration']
  },

  // Additional Business Continuity
  {
    id: 'f37',
    domain: 'Business Continuity',
    question: 'What is the difference between Availability Sets and Availability Zones?',
    answer: 'Availability Sets: protect against rack/network failures within a datacenter (99.95% SLA), use fault/update domains. Availability Zones: protect against entire datacenter failures (99.99% SLA), physically separate locations within region.',
    difficulty: 'hard',
    tags: ['Availability Sets', 'Availability Zones', 'HA']
  },
  {
    id: 'f38',
    domain: 'Business Continuity',
    question: 'What are Azure Storage account replication SLAs?',
    answer: 'LRS: 99.999999999% (11 nines). ZRS: 99.9999999999% (12 nines). GRS/RA-GRS: 99.99999999999999% (16 nines). GZRS/RA-GZRS: 99.99999999999999% (16 nines). Higher redundancy = higher durability.',
    difficulty: 'medium',
    tags: ['Storage', 'SLA', 'Redundancy']
  },
  {
    id: 'f39',
    domain: 'Business Continuity',
    question: 'What is Azure Traffic Manager?',
    answer: 'DNS-based traffic load balancer that distributes traffic globally. Routing methods: Priority, Weighted, Performance, Geographic, MultiValue, Subnet. Works at DNS level, not application level. Enables global HA and DR scenarios.',
    difficulty: 'medium',
    tags: ['Traffic Manager', 'DNS', 'Global Load Balancing']
  },
  {
    id: 'f40',
    domain: 'Business Continuity',
    question: 'What is the Azure Well-Architected Framework?',
    answer: 'Set of guiding principles for building quality cloud solutions. Five pillars: Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency. Includes design patterns, best practices, and assessment tools.',
    difficulty: 'medium',
    tags: ['Well-Architected', 'Best Practices', 'Architecture']
  },

  // Additional Infrastructure
  {
    id: 'f41',
    domain: 'Infrastructure',
    question: 'What is the difference between Azure App Service Plans?',
    answer: 'Free/Shared: shared infrastructure, no SLA. Basic: dedicated VMs, manual scale. Standard: auto-scale, staging slots, custom domains. Premium: enhanced performance, VNet integration. Isolated: dedicated environment, max scale, ASE.',
    difficulty: 'medium',
    tags: ['App Service', 'PaaS', 'Pricing']
  },
  {
    id: 'f42',
    domain: 'Infrastructure',
    question: 'What is Azure Service Bus?',
    answer: 'Enterprise messaging service with queues and pub/sub topics. Provides reliable message delivery, dead-letter queues, sessions, transactions, duplicate detection. Supports FIFO, at-least-once delivery. Use for decoupling applications.',
    difficulty: 'medium',
    tags: ['Service Bus', 'Messaging', 'Integration']
  },
  {
    id: 'f43',
    domain: 'Infrastructure',
    question: 'What is the difference between Azure Event Grid and Event Hub?',
    answer: 'Event Grid: reactive programming, event distribution service, pub-sub model, millions of events/sec, serverless. Event Hub: big data streaming, millions of events/sec, data ingestion, capture to storage, supports Kafka protocol.',
    difficulty: 'hard',
    tags: ['Event Grid', 'Event Hub', 'Messaging']
  },
  {
    id: 'f44',
    domain: 'Infrastructure',
    question: 'What is Azure API Management?',
    answer: 'Hybrid, multi-cloud API gateway. Features: API versioning, rate limiting, authentication, caching, monitoring, developer portal. Supports REST, SOAP, GraphQL. Tiers: Consumption, Developer, Basic, Standard, Premium.',
    difficulty: 'medium',
    tags: ['APIM', 'API Gateway', 'Integration']
  },
  {
    id: 'f45',
    domain: 'Infrastructure',
    question: 'What is Azure Logic Apps?',
    answer: 'Serverless workflow automation service. Low-code/no-code designer with 400+ connectors. Use for integrations, B2B scenarios, scheduling tasks. Consumption plan (pay-per-execution) or Standard plan (dedicated).',
    difficulty: 'easy',
    tags: ['Logic Apps', 'Workflow', 'Integration']
  },
  {
    id: 'f46',
    domain: 'Infrastructure',
    question: 'What are Azure VM sizes and series?',
    answer: 'General purpose (B,D): balanced CPU/memory. Compute optimized (F): high CPU/memory ratio. Memory optimized (E,M): high memory/CPU ratio. Storage optimized (L): high disk throughput. GPU (N): graphics/AI workloads. HPC (H): high-performance computing.',
    difficulty: 'medium',
    tags: ['Virtual Machines', 'Compute', 'Sizing']
  },
  {
    id: 'f47',
    domain: 'Infrastructure',
    question: 'What is Azure Container Apps?',
    answer: 'Serverless container platform built on Kubernetes. Auto-scales based on HTTP traffic, events, or CPU/memory. Supports microservices, event-driven apps, background jobs. Simpler than AKS, more flexible than App Service.',
    difficulty: 'medium',
    tags: ['Container Apps', 'Serverless', 'Containers']
  },
  {
    id: 'f48',
    domain: 'Infrastructure',
    question: 'What is Azure DDoS Protection?',
    answer: 'Two tiers: Basic (free, automatic) and Standard (paid, enhanced features). Standard provides attack analytics, alerting, mitigation tuning, rapid response, cost protection. Protects at network edge before traffic reaches resources.',
    difficulty: 'easy',
    tags: ['DDoS', 'Security', 'Networking']
  },
  {
    id: 'f49',
    domain: 'Infrastructure',
    question: 'What is Azure Firewall vs NSG?',
    answer: 'NSG: basic stateful packet filtering at subnet/NIC level, simple rules. Azure Firewall: fully stateful firewall service, FQDN filtering, threat intelligence, centralized logging, application/network rules, premium tier with TLS inspection.',
    difficulty: 'hard',
    tags: ['Firewall', 'NSG', 'Security']
  },
  {
    id: 'f50',
    domain: 'Infrastructure',
    question: 'What is Azure DNS?',
    answer: 'Hosting service for DNS domains using Azure infrastructure. Provides fast DNS responses, supports alias records, private DNS zones for VNet name resolution, DNSSEC (preview). Integrates with RBAC and Activity Log.',
    difficulty: 'easy',
    tags: ['DNS', 'Networking', 'Name Resolution']
  },

  // More Identity & Governance
  {
    id: 'f51',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What is Azure AD B2B vs B2C?',
    answer: 'B2B: invite external users (partners, vendors) to access internal apps, uses their existing identities. B2C: consumer-facing apps, millions of users, social/local accounts, customizable UI, supports CIAM scenarios.',
    difficulty: 'medium',
    tags: ['Azure AD', 'B2B', 'B2C']
  },
  {
    id: 'f52',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What is Azure Cost Management?',
    answer: 'Service for monitoring, allocating, and optimizing cloud costs. Features: cost analysis, budgets, alerts, recommendations, export data. Supports showback/chargeback with cost allocation. Works across Azure, AWS, and GCP.',
    difficulty: 'easy',
    tags: ['Cost Management', 'FinOps', 'Governance']
  },
  {
    id: 'f53',
    domain: 'Identity, Governance, and Monitoring',
    question: 'What are Azure built-in roles?',
    answer: 'Owner: full access including delegation. Contributor: full access except delegation. Reader: view only. Common specialized roles: Network Contributor, SQL DB Contributor, Virtual Machine Contributor, Monitoring Reader.',
    difficulty: 'easy',
    tags: ['RBAC', 'Roles', 'Security']
  },

  // More Data Storage
  {
    id: 'f54',
    domain: 'Data Storage',
    question: 'What is Azure SQL Database scaling options?',
    answer: 'DTU model: bundled measure (CPU/memory/IO). vCore model: independent scaling, reserved capacity discounts. Serverless: auto-pause during inactivity, auto-scale. Hyperscale: rapid scale-up, read replicas, fast restore.',
    difficulty: 'hard',
    tags: ['SQL Database', 'Scaling', 'Performance']
  },
  {
    id: 'f55',
    domain: 'Data Storage',
    question: 'What is Azure Blob Storage immutability?',
    answer: 'WORM (Write Once, Read Many) policies for compliance. Time-based retention: locked for specified period. Legal hold: indefinite retention until explicitly removed. Supports compliance with SEC, FINRA, etc.',
    difficulty: 'medium',
    tags: ['Blob Storage', 'Compliance', 'Immutability']
  },
  {
    id: 'f56',
    domain: 'Data Storage',
    question: 'What is change feed in Azure Storage?',
    answer: 'Provides transaction logs of changes to blobs and metadata. Captures create, modify, delete operations. Ordered, durable, immutable log. Use for event-driven architectures, auditing, replication scenarios.',
    difficulty: 'medium',
    tags: ['Change Feed', 'Blob Storage', 'Events']
  },

  // More Infrastructure
  {
    id: 'f57',
    domain: 'Infrastructure',
    question: 'What is Azure VPN Gateway types?',
    answer: 'PolicyBased: static routing, IKEv1, legacy. RouteBased: dynamic routing, IKEv2, supports multiple tunnels. SKUs: Basic, VpnGw1-5, VpnGw1-5AZ (zone redundant). Use RouteBased for production.',
    difficulty: 'medium',
    tags: ['VPN Gateway', 'Networking', 'Hybrid']
  },
  {
    id: 'f58',
    domain: 'Infrastructure',
    question: 'What is Azure Functions hosting plans?',
    answer: 'Consumption: true serverless, pay-per-execution, auto-scale. Premium: pre-warmed instances, VNet, unlimited duration. Dedicated: App Service Plan, predictable billing. Container Apps: event-driven containers.',
    difficulty: 'medium',
    tags: ['Functions', 'Serverless', 'Compute']
  },
  {
    id: 'f59',
    domain: 'Infrastructure',
    question: 'What is Azure Migrate?',
    answer: 'Hub for discovery, assessment, and migration to Azure. Tools: Server Assessment, Server Migration, Database Assessment, Database Migration, Web App Migration, Data Box. Supports VMware, Hyper-V, physical servers.',
    difficulty: 'easy',
    tags: ['Migration', 'Azure Migrate', 'Assessment']
  },
  {
    id: 'f60',
    domain: 'Infrastructure',
    question: 'What is Azure Content Delivery Network (CDN)?',
    answer: 'Global CDN solution for delivering content with low latency. Providers: Microsoft, Akamai, Verizon. Features: HTTPS support, query string caching, geo-filtering, compression, rules engine. Integrates with Azure services.',
    difficulty: 'easy',
    tags: ['CDN', 'Performance', 'Global Distribution']
  }
];
