import { NextRequest, NextResponse } from 'next/server';
import { Resend } from 'resend';

// Initialize Resend with API key (will be set via environment variable)
const resend = process.env.RESEND_API_KEY ? new Resend(process.env.RESEND_API_KEY) : null;

interface ContactFormData {
  name: string;
  email: string;
  company?: string;
  subject: string;
  message: string;
  interest: string;
}

const interestLabels: Record<string, string> = {
  general: 'General Inquiry',
  demo: 'Demo Request',
  pricing: 'Pricing Information',
  enterprise: 'Enterprise Solutions',
  partnership: 'Partnership',
  support: 'Technical Support',
};

export async function POST(request: NextRequest) {
  try {
    const body: ContactFormData = await request.json();

    // Validate required fields
    if (!body.name || !body.email || !body.subject || !body.message) {
      return NextResponse.json(
        { error: 'Missing required fields: name, email, subject, message' },
        { status: 400 }
      );
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(body.email)) {
      return NextResponse.json({ error: 'Invalid email format' }, { status: 400 });
    }

    // Build email content
    const emailHtml = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #7C3AED;">New Contact Form Submission</h2>

        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
          <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 12px 0; font-weight: bold; width: 150px;">Name:</td>
            <td style="padding: 12px 0;">${escapeHtml(body.name)}</td>
          </tr>
          <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 12px 0; font-weight: bold;">Email:</td>
            <td style="padding: 12px 0;">
              <a href="mailto:${escapeHtml(body.email)}">${escapeHtml(body.email)}</a>
            </td>
          </tr>
          ${
            body.company
              ? `
          <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 12px 0; font-weight: bold;">Company:</td>
            <td style="padding: 12px 0;">${escapeHtml(body.company)}</td>
          </tr>
          `
              : ''
          }
          <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 12px 0; font-weight: bold;">Interest:</td>
            <td style="padding: 12px 0;">${interestLabels[body.interest] || body.interest}</td>
          </tr>
          <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 12px 0; font-weight: bold;">Subject:</td>
            <td style="padding: 12px 0;">${escapeHtml(body.subject)}</td>
          </tr>
        </table>

        <div style="margin-top: 24px;">
          <h3 style="color: #333;">Message:</h3>
          <div style="background-color: #f5f5f5; padding: 16px; border-radius: 8px; white-space: pre-wrap;">
${escapeHtml(body.message)}
          </div>
        </div>

        <hr style="margin-top: 32px; border: none; border-top: 1px solid #eee;" />
        <p style="color: #666; font-size: 12px; margin-top: 16px;">
          This message was sent from the SQL2.AI contact form at ${new Date().toISOString()}
        </p>
      </div>
    `;

    const emailText = `
New Contact Form Submission
===========================

Name: ${body.name}
Email: ${body.email}
${body.company ? `Company: ${body.company}\n` : ''}Interest: ${interestLabels[body.interest] || body.interest}
Subject: ${body.subject}

Message:
${body.message}

---
Sent from SQL2.AI contact form at ${new Date().toISOString()}
    `.trim();

    // Send email via Resend if configured
    if (resend) {
      try {
        await resend.emails.send({
          from: 'SQL2.AI <noreply@sql2.ai>',
          to: ['info@servicevision.net'],
          replyTo: body.email,
          subject: `[SQL2.AI Contact] ${body.subject}`,
          html: emailHtml,
          text: emailText,
        });
      } catch (emailError) {
        console.error('Failed to send email via Resend:', emailError);
        // Log the submission even if email fails
        console.log('Contact form submission (email failed):', body);
      }
    } else {
      // Log submission when Resend is not configured (development mode)
      console.log('='.repeat(50));
      console.log('CONTACT FORM SUBMISSION (Resend not configured)');
      console.log('='.repeat(50));
      console.log('To: info@servicevision.net');
      console.log('From:', body.email);
      console.log('Subject:', body.subject);
      console.log('Interest:', interestLabels[body.interest] || body.interest);
      console.log('Company:', body.company || '(not provided)');
      console.log('Message:', body.message);
      console.log('='.repeat(50));
    }

    return NextResponse.json({
      success: true,
      message: 'Thank you for your message. We will get back to you within 24 hours.',
    });
  } catch (error) {
    console.error('Contact form error:', error);
    return NextResponse.json(
      { error: 'Failed to process your request. Please try again later.' },
      { status: 500 }
    );
  }
}

// Helper to escape HTML
function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
}
