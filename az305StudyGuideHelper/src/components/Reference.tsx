const Reference = () => {
  const domains = [
    {
      title: 'Design Identity, Governance, and Monitoring Solutions (25-30%)',
      topics: [
        {
          name: 'Azure Active Directory',
          items: [
            'Azure AD tenants, users, groups',
            'Azure AD B2B and B2C',
            'Conditional Access policies',
            'Privileged Identity Management (PIM)',
            'Identity Protection',
            'Multi-factor authentication (MFA)',
            'Managed identities for Azure resources'
          ]
        },
        {
          name: 'Governance',
          items: [
            'Management groups hierarchy',
            'Azure Policy (effects: deny, audit, append, modify, deployIfNotExists)',
            'Azure Blueprints',
            'Resource tags and naming conventions',
            'Azure Resource Manager (ARM) templates',
            'Role-based access control (RBAC)',
            'Custom roles and built-in roles'
          ]
        },
        {
          name: 'Monitoring',
          items: [
            'Azure Monitor (Metrics and Logs)',
            'Log Analytics and KQL queries',
            'Application Insights',
            'Network Watcher',
            'Azure Advisor',
            'Azure Service Health',
            'Action groups and alerts'
          ]
        }
      ]
    },
    {
      title: 'Design Data Storage Solutions (15-20%)',
      topics: [
        {
          name: 'Storage Accounts',
          items: [
            'Storage tiers: Hot, Cool, Archive',
            'Redundancy: LRS, ZRS, GRS, GZRS, RA-GRS, RA-GZRS',
            'Blob storage (block, append, page blobs)',
            'Azure Files and File Sync',
            'Storage security and encryption',
            'Lifecycle management policies',
            'Azure NetApp Files'
          ]
        },
        {
          name: 'Databases',
          items: [
            'Azure SQL Database (single, elastic pool)',
            'Azure SQL Managed Instance',
            'Azure Cosmos DB (APIs and consistency levels)',
            'Azure Database for PostgreSQL/MySQL',
            'Azure Synapse Analytics',
            'Azure Data Lake Storage Gen2',
            'Database scaling options (DTU vs vCore)'
          ]
        },
        {
          name: 'Data Integration',
          items: [
            'Azure Data Factory',
            'Azure Databricks',
            'Data migration strategies',
            'Hybrid data scenarios'
          ]
        }
      ]
    },
    {
      title: 'Design Business Continuity Solutions (15-20%)',
      topics: [
        {
          name: 'High Availability',
          items: [
            'Availability Sets (fault domains, update domains)',
            'Availability Zones',
            'Paired regions',
            'SLA calculations',
            'Load balancing options',
            'Auto-scaling strategies'
          ]
        },
        {
          name: 'Disaster Recovery',
          items: [
            'RTO and RPO objectives',
            'Azure Site Recovery',
            'Backup strategies',
            'Azure Backup (MARS, MABS)',
            'Database backup and restore',
            'Geo-replication for databases',
            'Recovery Services vault'
          ]
        }
      ]
    },
    {
      title: 'Design Infrastructure Solutions (30-35%)',
      topics: [
        {
          name: 'Compute',
          items: [
            'Virtual Machines (sizes, series)',
            'VM Scale Sets',
            'Azure Kubernetes Service (AKS)',
            'Azure Container Instances',
            'Azure App Service',
            'Azure Functions',
            'Azure Logic Apps',
            'Azure Batch'
          ]
        },
        {
          name: 'Networking',
          items: [
            'Virtual Networks (VNet)',
            'Subnets and IP addressing',
            'Network Security Groups (NSGs)',
            'Application Security Groups (ASGs)',
            'VNet peering and VPN Gateway',
            'Azure ExpressRoute',
            'Azure Load Balancer (Basic vs Standard)',
            'Azure Application Gateway and WAF',
            'Azure Front Door',
            'Azure Traffic Manager',
            'Azure Firewall',
            'Azure Bastion',
            'Service Endpoints vs Private Endpoints',
            'Azure Private Link',
            'Azure Virtual WAN',
            'DNS options (Azure DNS, Private DNS)'
          ]
        },
        {
          name: 'Migration',
          items: [
            'Azure Migrate',
            'Azure Database Migration Service',
            'Azure Import/Export service',
            'Azure Data Box',
            'Migration strategies (rehost, refactor, rearchitect)'
          ]
        }
      ]
    }
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-8">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          AZ-305 Exam Reference Guide
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Quick reference for all exam domains and key topics. Use this alongside flashcards and quizzes for comprehensive preparation.
        </p>

        <div className="space-y-8">
          {domains.map((domain, idx) => (
            <div key={idx} className="border-l-4 border-indigo-500 pl-6">
              <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200 mb-4">
                {domain.title}
              </h3>
              
              <div className="space-y-6">
                {domain.topics.map((topic, topicIdx) => (
                  <div key={topicIdx}>
                    <h4 className="font-semibold text-indigo-600 dark:text-indigo-400 mb-2">
                      {topic.name}
                    </h4>
                    <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {topic.items.map((item, itemIdx) => (
                        <li key={itemIdx} className="flex items-start text-sm text-gray-600 dark:text-gray-400">
                          <span className="mr-2 text-indigo-500">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-xl p-8 text-white">
        <h3 className="text-xl font-bold mb-4">Exam Information</h3>
        <div className="space-y-2 text-sm">
          <p><strong>Exam Code:</strong> AZ-305</p>
          <p><strong>Duration:</strong> 120 minutes</p>
          <p><strong>Question Format:</strong> Multiple choice, case studies, drag-and-drop</p>
          <p><strong>Passing Score:</strong> 700/1000</p>
          <p><strong>Validity:</strong> Certification valid for 1 year</p>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-8">
        <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200 mb-4">
          Recommended Resources
        </h3>
        <ul className="space-y-2 text-gray-600 dark:text-gray-400">
          <li>• Microsoft Learn - Free official learning paths</li>
          <li>• Azure documentation - In-depth technical documentation</li>
          <li>• Microsoft Certified: Azure Solutions Architect Expert page</li>
          <li>• Azure Architecture Center - Best practices and patterns</li>
          <li>• Practice with Azure free tier - Hands-on experience</li>
          <li>• Join Azure community forums and study groups</li>
        </ul>
      </div>
    </div>
  );
};

export default Reference;
