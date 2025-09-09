import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

// Validation schema
const contactSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email address'),
  company: z.string().optional(),
  type: z.enum(['buyer', 'investor', 'farmer', 'other']),
  message: z.string().min(10, 'Message must be at least 10 characters'),
  consent: z.boolean().refine((val) => val === true, {
    message: 'You must accept the privacy policy',
  }),
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate the request body
    const validatedData = contactSchema.parse(body)
    
    // Here you would integrate with your email service (SendGrid, SES, etc.)
    // For now, we'll just log the data and return success
    console.log('Contact form submission:', validatedData)
    
    // Example integration with email service:
    // await sendEmail({
    //   to: process.env.CONTACT_EMAIL || 'info@greenstemglobal.com',
    //   subject: `New ${validatedData.type} inquiry from ${validatedData.name}`,
    //   html: formatEmailTemplate(validatedData),
    // })
    
    // Store in database if needed
    // await saveContactSubmission(validatedData)
    
    return NextResponse.json(
      { success: true, message: 'Message sent successfully' },
      { status: 200 }
    )
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: error.errors[0].message },
        { status: 400 }
      )
    }
    
    console.error('Contact form error:', error)
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    )
  }
}

// Helper function to format email (example)
function formatEmailTemplate(data: z.infer<typeof contactSchema>) {
  return `
    <h2>New Contact Form Submission</h2>
    <p><strong>Name:</strong> ${data.name}</p>
    <p><strong>Email:</strong> ${data.email}</p>
    <p><strong>Company:</strong> ${data.company || 'Not provided'}</p>
    <p><strong>Type:</strong> ${data.type}</p>
    <p><strong>Message:</strong></p>
    <p>${data.message}</p>
    <hr>
    <p><small>User has consented to data processing.</small></p>
  `
}
