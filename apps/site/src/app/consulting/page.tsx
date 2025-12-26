import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../components/marketing';

export const metadata: Metadata = {
  title: 'Database & AI Consulting - SQL2.AI',
  description:
    'Expert consulting at the intersection of AI, database development, compliance, and DBA practices. Transform your database operations with intelligent automation.',
};

const convergenceAreas = [
  {
    title: 'AI-Powered Database Development',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
    </svg>`,
    description:
      'Leverage large language models to accelerate SQL development, generate optimized queries, and automate repetitive database tasks. Our consultants help you implement AI-assisted workflows that reduce development time by 60%.',
    capabilities: [
      'Natural language to SQL generation',
      'Automated stored procedure creation',
      'AI-driven code review and optimization',
      'Intelligent migration planning',
    ],
  },
  {
    title: 'Compliance & Regulatory Automation',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
    </svg>`,
    description:
      'Navigate complex regulatory requirements with automated compliance scanning. We help organizations achieve and maintain SOC 2, HIPAA, GDPR, and PCI-DSS compliance through continuous monitoring and intelligent alerting.',
    capabilities: [
      'Automated PII/PHI detection',
      'Continuous compliance monitoring',
      'Audit trail automation',
      'Regulatory report generation',
    ],
  },
  {
    title: 'Modern DBA Transformation',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
    </svg>`,
    description:
      'Transform traditional DBA roles into AI-augmented positions that deliver 10x the value. We help teams adopt proactive monitoring, predictive analytics, and self-healing database systems.',
    capabilities: [
      'Predictive performance tuning',
      'Automated incident response',
      'Capacity planning with ML',
      'Self-optimizing query engines',
    ],
  },
  {
    title: 'Intelligent Data Operations',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5" />
    </svg>`,
    description:
      'Unify your data operations with AI-driven orchestration across SQL Server, PostgreSQL, and hybrid environments. Our approach ensures consistency, reliability, and intelligent automation at scale.',
    capabilities: [
      'Cross-platform query optimization',
      'Unified monitoring dashboards',
      'Automated schema synchronization',
      'Intelligent load balancing',
    ],
  },
];

const engagementTypes = [
  {
    name: 'Strategic Assessment',
    duration: '2-4 weeks',
    description:
      'Comprehensive evaluation of your database infrastructure, identifying opportunities for AI integration, compliance gaps, and operational improvements.',
    deliverables: [
      'Current state analysis',
      'AI readiness scorecard',
      'Compliance gap assessment',
      'Prioritized roadmap',
      'ROI projections',
    ],
  },
  {
    name: 'Implementation Sprint',
    duration: '6-12 weeks',
    description:
      'Hands-on implementation of AI-powered database solutions, from initial setup through production deployment and knowledge transfer.',
    deliverables: [
      'Solution architecture',
      'Configured SQL2.AI deployment',
      'Custom integrations',
      'Team training',
      'Runbooks & documentation',
    ],
  },
  {
    name: 'Managed Transformation',
    duration: '3-12 months',
    description:
      'End-to-end transformation program that modernizes your entire database development lifecycle with continuous support and optimization.',
    deliverables: [
      'Phased implementation plan',
      'Ongoing optimization',
      'Quarterly business reviews',
      'Dedicated success manager',
      'Priority support access',
    ],
  },
];

const industries = [
  {
    name: 'Financial Services',
    challenges: ['SOC 2 & PCI-DSS compliance', 'High-frequency transaction optimization', 'Fraud detection data pipelines'],
  },
  {
    name: 'Healthcare',
    challenges: ['HIPAA compliance automation', 'PHI detection & protection', 'Clinical data integration'],
  },
  {
    name: 'Technology',
    challenges: ['Multi-tenant database scaling', 'CI/CD pipeline integration', 'Developer productivity'],
  },
  {
    name: 'E-Commerce',
    challenges: ['Peak load optimization', 'Real-time inventory sync', 'Customer data protection'],
  },
];

const teamExpertise = [
  {
    area: 'Database Engineering',
    years: '20+',
    description: 'Deep expertise in SQL Server and PostgreSQL architecture, performance tuning, and high-availability configurations.',
  },
  {
    area: 'AI/ML Implementation',
    years: '8+',
    description: 'Practical experience deploying LLMs, building agentic systems, and integrating AI into enterprise workflows.',
  },
  {
    area: 'Compliance & Security',
    years: '15+',
    description: 'Hands-on experience with SOC 2, HIPAA, GDPR, and PCI-DSS audits and remediation programs.',
  },
  {
    area: 'Enterprise Architecture',
    years: '18+',
    description: 'Track record of designing and implementing scalable data platforms for Fortune 500 companies.',
  },
];

export default function ConsultingPage(): JSX.Element {
  return (
    <>
      {/* Hero Section */}
      <section className="pt-32 pb-16 md:pt-40 md:pb-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5" />
        <div className="container-wide relative">
          <div className="max-w-4xl mx-auto text-center">
            <span className="inline-block px-4 py-2 rounded-full bg-primary/10 text-primary text-small font-medium mb-6">
              Expert Database & AI Consulting
            </span>
            <h1 className="text-h1 text-text-primary mb-6">
              The Convergence of{' '}
              <span className="gradient-text">AI, Databases & Compliance</span>
            </h1>
            <p className="text-xl text-text-secondary mb-8 max-w-3xl mx-auto">
              We help organizations navigate the transformative intersection of artificial intelligence,
              modern database development, regulatory compliance, and evolved DBA practices.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link href="/contact" className="btn-primary">
                Schedule a Consultation
              </Link>
              <Link href="#approach" className="btn-secondary">
                Our Approach
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* The Convergence */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="text-h2 text-text-primary mb-4">
              Four Forces Reshaping Database Operations
            </h2>
            <p className="text-lg text-text-secondary">
              The traditional boundaries between development, operations, compliance, and AI are dissolving.
              Organizations that master this convergence gain unprecedented competitive advantage.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            {convergenceAreas.map((area) => (
              <div key={area.title} className="card p-8">
                <div
                  className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-6 text-primary"
                  dangerouslySetInnerHTML={{ __html: area.icon }}
                />
                <h3 className="text-h4 text-text-primary mb-4">{area.title}</h3>
                <p className="text-text-secondary mb-6">{area.description}</p>
                <ul className="space-y-2">
                  {area.capabilities.map((cap) => (
                    <li key={cap} className="flex items-center gap-3 text-small text-text-secondary">
                      <svg className="w-5 h-5 text-success shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {cap}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why This Matters Now */}
      <section id="approach" className="section">
        <div className="container-wide">
          <div className="max-w-5xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <span className="inline-block px-3 py-1 rounded-full bg-warning/10 text-warning text-small font-medium mb-4">
                  The Urgency
                </span>
                <h2 className="text-h2 text-text-primary mb-6">
                  Why Organizations Are Acting Now
                </h2>
                <div className="space-y-6 text-text-secondary">
                  <p>
                    <strong className="text-text-primary">AI is disrupting database work.</strong> Development teams are
                    already using ChatGPT and Claude for SQL queries—often without proper governance, security review,
                    or optimization. Organizations that don&apos;t formalize AI-assisted database development will face
                    technical debt, security vulnerabilities, and compliance gaps.
                  </p>
                  <p>
                    <strong className="text-text-primary">Compliance requirements are accelerating.</strong> New privacy
                    regulations, AI governance requirements, and data residency rules are being enacted globally.
                    Manual compliance processes can&apos;t scale—automation is the only path forward.
                  </p>
                  <p>
                    <strong className="text-text-primary">DBA talent is evolving.</strong> The next generation of
                    database professionals expects AI-augmented tooling. Organizations that invest in modern practices
                    attract and retain top talent while increasing productivity 5-10x.
                  </p>
                </div>
              </div>
              <div className="card p-8 bg-gradient-to-br from-bg-surface to-bg-base">
                <h3 className="text-h4 text-text-primary mb-6">The Transformation Opportunity</h3>
                <div className="space-y-6">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center shrink-0 text-primary font-bold">
                      60%
                    </div>
                    <div>
                      <p className="font-medium text-text-primary">Faster Development</p>
                      <p className="text-small text-text-muted">AI-generated SQL and automated migrations</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-full bg-success/10 flex items-center justify-center shrink-0 text-success font-bold">
                      80%
                    </div>
                    <div>
                      <p className="font-medium text-text-primary">Compliance Automation</p>
                      <p className="text-small text-text-muted">Continuous scanning replaces manual audits</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-full bg-secondary/10 flex items-center justify-center shrink-0 text-secondary font-bold">
                      10x
                    </div>
                    <div>
                      <p className="font-medium text-text-primary">DBA Productivity</p>
                      <p className="text-small text-text-muted">Self-healing systems and predictive ops</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-full bg-warning/10 flex items-center justify-center shrink-0 text-warning font-bold">
                      90%
                    </div>
                    <div>
                      <p className="font-medium text-text-primary">Fewer Incidents</p>
                      <p className="text-small text-text-muted">Predictive monitoring catches issues early</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Engagement Types */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-h2 text-text-primary mb-4">Engagement Models</h2>
            <p className="text-lg text-text-secondary">
              Flexible consulting engagements tailored to your organization&apos;s maturity and objectives.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {engagementTypes.map((engagement, index) => (
              <div
                key={engagement.name}
                className={`card p-8 ${index === 1 ? 'border-primary/50 ring-1 ring-primary/20' : ''}`}
              >
                {index === 1 && (
                  <span className="inline-block px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium mb-4">
                    Most Popular
                  </span>
                )}
                <h3 className="text-h4 text-text-primary mb-2">{engagement.name}</h3>
                <p className="text-primary font-medium mb-4">{engagement.duration}</p>
                <p className="text-text-secondary text-small mb-6">{engagement.description}</p>
                <div>
                  <p className="text-small font-medium text-text-primary mb-3">Deliverables:</p>
                  <ul className="space-y-2">
                    {engagement.deliverables.map((item) => (
                      <li key={item} className="flex items-center gap-2 text-small text-text-muted">
                        <svg className="w-4 h-4 text-primary shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Industry Expertise */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-h2 text-text-primary mb-4">Industry Expertise</h2>
            <p className="text-lg text-text-secondary">
              We understand the unique database and compliance challenges across industries.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {industries.map((industry) => (
              <div key={industry.name} className="card p-6">
                <h3 className="text-h5 text-text-primary mb-4">{industry.name}</h3>
                <ul className="space-y-2">
                  {industry.challenges.map((challenge) => (
                    <li key={challenge} className="text-small text-text-secondary flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 shrink-0" />
                      {challenge}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team Expertise */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-h2 text-text-primary mb-4">Our Expertise</h2>
            <p className="text-lg text-text-secondary">
              Decades of combined experience across database engineering, AI, and enterprise security.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {teamExpertise.map((exp) => (
              <div key={exp.area} className="text-center p-6">
                <div className="text-4xl font-bold text-primary mb-2">{exp.years}</div>
                <div className="text-small font-medium text-text-muted mb-2">Years Experience</div>
                <h3 className="text-h5 text-text-primary mb-3">{exp.area}</h3>
                <p className="text-small text-text-secondary">{exp.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Process */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-h2 text-text-primary mb-4">How We Work</h2>
            <p className="text-lg text-text-secondary">
              A proven methodology for AI-powered database transformation.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-border hidden md:block" />

              {[
                {
                  step: '01',
                  title: 'Discovery & Assessment',
                  description: 'We analyze your current database infrastructure, development workflows, compliance posture, and team capabilities to understand the full landscape.',
                },
                {
                  step: '02',
                  title: 'Strategy & Roadmap',
                  description: 'Based on your goals and constraints, we design a phased implementation plan with clear milestones, dependencies, and success metrics.',
                },
                {
                  step: '03',
                  title: 'Implementation',
                  description: 'Our team works alongside yours to deploy solutions, integrate with existing systems, and ensure knowledge transfer at every step.',
                },
                {
                  step: '04',
                  title: 'Optimization & Support',
                  description: 'We continue to monitor, tune, and optimize your environment while providing ongoing support and quarterly business reviews.',
                },
              ].map((phase) => (
                <div key={phase.step} className="relative flex gap-8 mb-12 last:mb-0">
                  <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center text-white font-bold text-lg shrink-0 relative z-10">
                    {phase.step}
                  </div>
                  <div className="pt-3">
                    <h3 className="text-h4 text-text-primary mb-2">{phase.title}</h3>
                    <p className="text-text-secondary">{phase.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Testimonial/Case Study Preview */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <div className="card p-8 md:p-12 bg-gradient-to-br from-primary/5 to-transparent">
              <blockquote className="text-xl md:text-2xl text-text-primary mb-6 italic">
                &ldquo;SQL2.AI&apos;s consulting team helped us transform our database operations from reactive
                firefighting to proactive, AI-driven management. We&apos;ve reduced incidents by 85% while
                achieving SOC 2 Type II certification in half the expected time.&rdquo;
              </blockquote>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
                  VP
                </div>
                <div>
                  <p className="font-medium text-text-primary">VP of Engineering</p>
                  <p className="text-small text-text-muted">Series B FinTech Company</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready to Transform Your Database Operations?"
        description="Schedule a free 30-minute consultation to discuss your challenges and explore how AI-powered database management can accelerate your organization."
        primaryCTA={{ text: 'Schedule Consultation', href: '/contact' }}
        secondaryCTA={{ text: 'View Case Studies', href: '/blog' }}
      />
    </>
  );
}
