import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Containerize - Database to Docker/Kubernetes | SQL2.AI',
  description:
    'Automate database containerization from on-prem or cloud to Docker and Kubernetes with zero-downtime migration.',
};

export default function ContainerizePage(): JSX.Element {
  return (
    <>
      {/* Hero */}
      <section className="pt-32 pb-16 md:pt-40 md:pb-20">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <Link
              href="/features/"
              className="inline-flex items-center gap-2 text-small text-text-muted hover:text-text-secondary mb-6"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              All Modules
            </Link>

            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-2xl bg-[#06B6D4]/10 flex items-center justify-center text-[#06B6D4]">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Containerize</h1>
                <p className="text-lg text-[#06B6D4] font-medium">Docker & Kubernetes Migration</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Automate database containerization from on-prem or cloud instances to Docker and Kubernetes.
              Support for Azure ACS, AWS EC2, and GCP with zero-downtime migration.
            </p>
          </div>
        </div>
      </section>

      {/* Target Platforms */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Target Platforms</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="card p-6 text-center">
              <div className="text-4xl mb-4">🐳</div>
              <h3 className="text-h5 text-text-primary mb-2">Docker</h3>
              <p className="text-sm text-text-muted">Standalone containers with optimized images</p>
            </div>
            <div className="card p-6 text-center">
              <div className="text-4xl mb-4">☸️</div>
              <h3 className="text-h5 text-text-primary mb-2">Kubernetes</h3>
              <p className="text-sm text-text-muted">StatefulSets, PVCs, and operator patterns</p>
            </div>
            <div className="card p-6 text-center">
              <div className="text-4xl mb-4">☁️</div>
              <h3 className="text-h5 text-text-primary mb-2">Managed K8s</h3>
              <p className="text-sm text-text-muted">AKS, EKS, GKE with cloud-native storage</p>
            </div>
          </div>
        </div>
      </section>

      {/* Migration Process */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Migration Process</h2>

          <div className="max-w-4xl mx-auto space-y-6">
            {[
              { step: 1, title: 'Analyze', desc: 'Scan source database for size, dependencies, and compatibility' },
              { step: 2, title: 'Configure', desc: 'Generate Dockerfile, Helm charts, and Kubernetes manifests' },
              { step: 3, title: 'Build', desc: 'Create optimized container images with your data' },
              { step: 4, title: 'Test', desc: 'Validate container in staging environment' },
              { step: 5, title: 'Deploy', desc: 'Zero-downtime cutover with data sync' },
              { step: 6, title: 'Monitor', desc: 'Integrated health checks and alerting' },
            ].map((item) => (
              <div key={item.step} className="card p-4 flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-[#06B6D4] text-white flex items-center justify-center font-bold shrink-0">
                  {item.step}
                </div>
                <div>
                  <h3 className="text-h6 text-text-primary">{item.title}</h3>
                  <p className="text-sm text-text-muted">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Generated Artifacts */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Generated Artifacts</h2>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Docker</h3>
              <ul className="space-y-2 text-text-secondary text-sm">
                <li>• Optimized Dockerfile for SQL Server/PostgreSQL</li>
                <li>• docker-compose.yml with volumes and networks</li>
                <li>• Health check scripts</li>
                <li>• Backup/restore scripts</li>
                <li>• Environment configuration</li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Kubernetes</h3>
              <ul className="space-y-2 text-text-secondary text-sm">
                <li>• StatefulSet manifests</li>
                <li>• PersistentVolumeClaims</li>
                <li>• Secrets and ConfigMaps</li>
                <li>• Service definitions</li>
                <li>• Helm charts (optional)</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Sample Output */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Sample Kubernetes Manifest</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`# Generated by SQL Containerize
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: sqlserver-production
spec:
  serviceName: sqlserver
  replicas: 1
  template:
    spec:
      containers:
      - name: sqlserver
        image: mcr.microsoft.com/mssql/server:2022-latest
        env:
        - name: ACCEPT_EULA
          value: "Y"
        - name: SA_PASSWORD
          valueFrom:
            secretKeyRef:
              name: sqlserver-secret
              key: password
        volumeMounts:
        - name: data
          mountPath: /var/opt/mssql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready to Containerize?"
        description="Migrate your databases to Docker and Kubernetes with automated manifests and zero-downtime deployment."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
