import { Metadata } from 'next';
import Link from 'next/link';
import { getAllPosts } from '@/lib/blog';

export const metadata: Metadata = {
  title: 'Blog - SQL2.AI',
  description:
    'Educational articles on database development, AI-powered SQL tools, performance optimization, compliance, and more.',
};

export default async function BlogPage() {
  const posts = await getAllPosts();

  // Group posts by category
  const categories = posts.reduce(
    (acc, post) => {
      const category = post.category || 'General';
      if (!acc[category]) acc[category] = [];
      acc[category].push(post);
      return acc;
    },
    {} as Record<string, typeof posts>
  );

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="py-20 md:py-32 bg-gradient-to-b from-bg-surface to-bg-primary">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-h1 mb-6">
              SQL2.AI <span className="gradient-text">Blog</span>
            </h1>
            <p className="text-xl text-text-secondary mb-8 max-w-2xl mx-auto">
              Educational articles on database development, AI-powered SQL tools, performance
              optimization, compliance, and best practices.
            </p>
          </div>
        </div>
      </section>

      {/* Featured Post */}
      {posts.length > 0 && posts[0].featured && (
        <section className="py-12 bg-bg-primary">
          <div className="container">
            <div className="max-w-4xl mx-auto">
              <Link href={`/blog/${posts[0].slug}`} className="block group">
                <div className="card p-8 hover:border-primary/50 transition-all">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-xs font-mono bg-primary/20 text-primary px-2 py-1 rounded">
                      Featured
                    </span>
                    <span className="text-xs text-text-muted">{posts[0].category}</span>
                    <span className="text-xs text-text-muted">
                      {new Date(posts[0].date).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                    </span>
                  </div>
                  <h2 className="text-h2 mb-4 group-hover:text-primary transition-colors">
                    {posts[0].title}
                  </h2>
                  <p className="text-text-secondary mb-4">{posts[0].excerpt}</p>
                  <span className="text-primary font-medium">Read more →</span>
                </div>
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* All Posts by Category */}
      <section className="py-20 bg-bg-surface">
        <div className="container">
          <div className="max-w-6xl mx-auto">
            {Object.entries(categories).map(([category, categoryPosts]) => (
              <div key={category} className="mb-16 last:mb-0">
                <h2 className="text-h3 mb-8 pb-4 border-b border-border">{category}</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {categoryPosts.map((post) => (
                    <Link key={post.slug} href={`/blog/${post.slug}`} className="block group">
                      <article className="card p-6 h-full hover:border-primary/50 transition-all">
                        <div className="flex items-center gap-2 mb-3">
                          <span className="text-xs text-text-muted">
                            {new Date(post.date).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                            })}
                          </span>
                          {post.readTime && (
                            <span className="text-xs text-text-muted">{post.readTime}</span>
                          )}
                        </div>
                        <h3 className="text-h5 mb-3 group-hover:text-primary transition-colors">
                          {post.title}
                        </h3>
                        <p className="text-small text-text-secondary line-clamp-3">
                          {post.excerpt}
                        </p>
                        {post.tags && post.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-4">
                            {post.tags.slice(0, 3).map((tag) => (
                              <span
                                key={tag}
                                className="text-xs bg-bg-primary px-2 py-1 rounded text-text-muted"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </article>
                    </Link>
                  ))}
                </div>
              </div>
            ))}

            {posts.length === 0 && (
              <div className="text-center py-20">
                <p className="text-text-secondary text-lg mb-4">No blog posts yet.</p>
                <p className="text-text-muted">Check back soon for educational content!</p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Newsletter CTA */}
      <section className="py-20 bg-bg-primary">
        <div className="container">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-h2 mb-4">Stay Updated</h2>
            <p className="text-text-secondary mb-8">
              Get the latest articles on database development and AI-powered SQL tools delivered to
              your inbox.
            </p>
            <Link href="/contact" className="btn-primary">
              Subscribe to Updates
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
