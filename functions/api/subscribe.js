/**
 * Cloudflare Pages Function to handle newsletter subscriptions via Kit (ConvertKit) API
 * 
 * API Endpoint: /api/subscribe
 * Method: POST
 * Body: { email: string }
 */

export async function onRequestPost(context) {
  // Get environment variables (set in Cloudflare Pages dashboard)
  const KIT_API_KEY = context.env.KIT_API_KEY;
  const KIT_FORM_ID = '9030749'; // Clare form ID

  // CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': 'https://gilgatson.com',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  // Handle preflight OPTIONS request
  if (context.request.method === 'OPTIONS') {
    return new Response(null, {
      headers: corsHeaders,
    });
  }

  try {
    // Parse request body
    const { email } = await context.request.json();

    // Validate email
    if (!email || !email.includes('@')) {
      return new Response(
        JSON.stringify({ error: 'Invalid email address' }),
        {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            ...corsHeaders,
          },
        }
      );
    }

    // Check if API key is set
    if (!KIT_API_KEY) {
      console.error('Kit API key not configured');
      return new Response(
        JSON.stringify({ error: 'Server configuration error' }),
        {
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            ...corsHeaders,
          },
        }
      );
    }

    // Subscribe to Kit using V3 API (form endpoint)
    // Kit API v3 uses api_key in the request body, not Bearer token
    const kitResponse = await fetch(`https://api.convertkit.com/v3/forms/${KIT_FORM_ID}/subscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
      },
      body: JSON.stringify({
        api_key: KIT_API_KEY,
        email: email,
      }),
    });

    const kitData = await kitResponse.json();

    if (!kitResponse.ok) {
      console.error('Kit API error:', kitData);
      return new Response(
        JSON.stringify({ 
          error: 'Failed to subscribe. Please try again later.',
          details: kitData.message || 'Unknown error'
        }),
        {
          status: kitResponse.status,
          headers: {
            'Content-Type': 'application/json',
            ...corsHeaders,
          },
        }
      );
    }

    // Success
    return new Response(
      JSON.stringify({ 
        success: true,
        message: 'Successfully subscribed to the newsletter!',
        subscriber_id: kitData.subscription?.subscriber?.id
      }),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders,
        },
      }
    );

  } catch (error) {
    console.error('Subscription error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'An unexpected error occurred. Please try again later.',
        details: error.message
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders,
        },
      }
    );
  }
}
