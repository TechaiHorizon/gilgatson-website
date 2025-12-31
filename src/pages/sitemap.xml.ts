export async function GET() {
  const pages = [
    { url: '', priority: '1.0', changefreq: 'weekly' },
    { url: 'about', priority: '0.8', changefreq: 'monthly' },
    { url: 'books', priority: '0.8', changefreq: 'monthly' },
    { url: 'blog', priority: '0.9', changefreq: 'weekly' },
    { url: 'blog/america-losing-ai-race', priority: '0.9', changefreq: 'monthly' },
    { url: 'blog/energy-the-real-bottleneck-for-ai', priority: '0.9', changefreq: 'monthly' },
    { url: 'contact', priority: '0.7', changefreq: 'monthly' },
  ];
  
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${pages.map(page => `  <url>
    <loc>https://gilgatson.com/${page.url}</loc>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`).join('\n')}
</urlset>`;

  return new Response(sitemap, {
    headers: {
      'Content-Type': 'application/xml',
    },
  });
}
