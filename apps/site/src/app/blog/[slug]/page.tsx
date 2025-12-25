import { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getAllPosts, getPostBySlug } from '@/lib/blog';
import { MDXContent } from '@/components/blog/MDXContent';

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPostBySlug(slug);

  if (!post) {
    return {
      title: 'Post Not Found - SQL2.AI Blog',
    };
  }

  return {
    title: `${post.title} - SQL2.AI Blog`,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
      publishedTime: post.date,
      authors: [post.author],
      tags: post.tags,
    },
  };
}

export async function generateStaticParams() {
  const posts = await getAllPosts();
  return posts.map((post) => ({
    slug: post.slug,
  }));
}

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params;
  const post = await getPostBySlug(slug);

  if (!post) {
    notFound();
  }

  // Get related posts (same category, excluding current)
  const allPosts = await getAllPosts();
  const relatedPosts = allPosts
    .filter((p) => p.slug !== post.slug && p.category === post.category)
    .slice(0, 3);

  return (
    <main className="min-h-screen">
      {/* Article Header */}
      <section className="py-16 md:py-24 bg-gradient-to-b from-bg-surface to-bg-primary">
        <div className="container">
          <div className="max-w-3xl mx-auto">
            <Link
              href="/blog"
              className="inline-flex items-center gap-2 text-text-muted hover:text-primary mb-8 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              Back to Blog
            </Link>

            <div className="flex items-center gap-3 mb-6">
              <span className="text-sm font-mono bg-primary/20 text-primary px-3 py-1 rounded">
                {post.category}
              </span>
              <span className="text-sm text-text-muted">{post.readTime}</span>
            </div>

            <h1 className="text-h1 mb-6">{post.title}</h1>

            <p className="text-xl text-text-secondary mb-8">{post.excerpt}</p>

            <div className="flex items-center gap-4 text-sm text-text-muted">
              <span>By {post.author}</span>
              <span>•</span>
              <time dateTime={post.date}>
                {new Date(post.date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </time>
            </div>
          </div>
        </div>
      </section>

      {/* Article Content */}
      <section className="py-16 bg-bg-primary">
        <div className="container">
          <div className="max-w-3xl mx-auto">
            <article className="prose prose-invert prose-lg max-w-none">
              <MDXContent content={post.content} />
            </article>

            {/* Tags */}
            {post.tags && post.tags.length > 0 && (
              <div className="mt-12 pt-8 border-t border-border">
                <h4 className="text-sm font-medium text-text-muted mb-4">Tags</h4>
                <div className="flex flex-wrap gap-2">
                  {post.tags.map((tag) => (
                    <Link
                      key={tag}
                      href={`/blog?tag=${encodeURIComponent(tag)}`}
                      className="text-sm bg-bg-surface px-3 py-1 rounded hover:bg-primary/20 hover:text-primary transition-colors"
                    >
                      {tag}
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Related Posts */}
      {relatedPosts.length > 0 && (
        <section className="py-16 bg-bg-surface">
          <div className="container">
            <div className="max-w-5xl mx-auto">
              <h2 className="text-h3 mb-8">Related Articles</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {relatedPosts.map((relatedPost) => (
                  <Link
                    key={relatedPost.slug}
                    href={`/blog/${relatedPost.slug}`}
                    className="block group"
                  >
                    <article className="card p-6 h-full hover:border-primary/50 transition-all">
                      <div className="text-xs text-text-muted mb-3">
                        {new Date(relatedPost.date).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </div>
                      <h3 className="text-h5 mb-3 group-hover:text-primary transition-colors">
                        {relatedPost.title}
                      </h3>
                      <p className="text-small text-text-secondary line-clamp-2">
                        {relatedPost.excerpt}
                      </p>
                    </article>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* CTA */}
      <section className="py-16 bg-bg-primary">
        <div className="container">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-h3 mb-4">Ready to Transform Your Database Workflow?</h2>
            <p className="text-text-secondary mb-8">
              See how SQL2.AI can automate and enhance your database development.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/contact" className="btn-primary">
                Get Started
              </Link>
              <Link href="/features" className="btn-secondary">
                Explore Features
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
