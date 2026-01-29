import type { APIRoute } from 'astro';

export const GET: APIRoute = async () => {
  // Get all blog posts dynamically
  const posts = await import.meta.glob('./blog/*.md', { eager: true });
  
  const postUrls = Object.entries(posts).map(([path, post]: [string, any]) => {
    const slug = path.replace('./blog/', '').replace('.md', '');
    const pubDate = post.frontmatter?.pubDate || new Date().toISOString();
    
    return `  <url>
    <loc>https://gilgatson.com/blog/${slug}</loc>
    <lastmod>${new Date(pubDate).toISOString().split('T')[0]}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>`;
  }).join('\n');
  
  const staticPages = [
    { url: '', priority: '1.0', changefreq: 'daily' },
    { url: 'about', priority: '0.8', changefreq: 'monthly' },
    { url: 'books', priority: '0.8', changefreq: 'monthly' },
    { url: 'blog', priority: '0.9', changefreq: 'daily' },
    { url: 'contact', priority: '0.7', changefreq: 'monthly' },
  ];
  
  const staticUrls = staticPages.map(page => `  <url>
    <loc>https://gilgatson.com/${page.url}</loc>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`).join('\n');
  
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${staticUrls}
${postUrls}
</urlset>`;

  return new Response(sitemap, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8'
    }
  });
};
