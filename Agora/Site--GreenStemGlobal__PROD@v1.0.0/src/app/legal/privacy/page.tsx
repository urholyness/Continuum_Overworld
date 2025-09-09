export const metadata = {
  title: 'Privacy Policy',
  description: 'Privacy policy and data protection information for GreenStemGlobal.',
}

export default function PrivacyPage() {
  return (
    <div className="py-20 bg-white">
      <div className="container">
        <div className="max-w-3xl mx-auto prose prose-lg">
          <h1 className="text-3xl font-display font-bold mb-8">Privacy Policy</h1>
          
          <p className="text-gray-600 mb-8">
            Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
          </p>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">1. Data Protection at a Glance</h2>
            
            <h3 className="text-lg font-semibold mt-4 mb-2">General Information</h3>
            <p>
              The following information provides a simple overview of what happens to your personal 
              data when you visit this website. Personal data is any data that can be used to 
              personally identify you. Detailed information on data protection can be found in our 
              privacy policy listed below this text.
            </p>

            <h3 className="text-lg font-semibold mt-4 mb-2">Data Collection on This Website</h3>
            <p>
              <strong>Who is responsible for data collection on this website?</strong><br />
              Data processing on this website is carried out by the website operator. You can find 
              the operator's contact details in the "Controller" section of this privacy policy.
            </p>

            <p className="mt-3">
              <strong>How do we collect your data?</strong><br />
              Your data is collected when you provide it to us. This could be data that you enter 
              into a contact form, for example. Other data is collected automatically or with your 
              consent when you visit the website by our IT systems. This is primarily technical data 
              (e.g., internet browser, operating system, or time of page access). This data is 
              collected automatically as soon as you enter this website.
            </p>

            <p className="mt-3">
              <strong>What do we use your data for?</strong><br />
              Some of the data is collected to ensure the proper functioning of the website. Other 
              data may be used to analyze your user behavior.
            </p>

            <p className="mt-3">
              <strong>What rights do you have regarding your data?</strong><br />
              You always have the right to request information about your stored data, its origin, 
              its recipients, and the purpose of its collection at no charge. You also have the right 
              to request that it be corrected or deleted. If you have further questions about privacy 
              and data protection, you can contact us at any time.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">2. Controller</h2>
            <p>
              The controller responsible for data processing on this website is:
            </p>
            <p className="mt-3">
              GreenStemGlobal GmbH<br />
              Friedrichstraße 123<br />
              10117 Berlin<br />
              Germany<br />
              Phone: +49 30 1234 5678<br />
              Email: privacy@greenstemglobal.com
            </p>
            <p className="mt-3">
              The controller is the natural or legal person who alone or jointly with others decides 
              on the purposes and means of processing personal data (e.g., names, email addresses, etc.).
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">3. Data Collection on This Website</h2>
            
            <h3 className="text-lg font-semibold mt-4 mb-2">Cookies</h3>
            <p>
              Our website uses cookies. Cookies are small text files that are stored on your device 
              by your browser. They do not cause any damage. We use cookies to make our offer 
              user-friendly. Some cookies remain stored on your device until you delete them. They 
              allow us to recognize your browser on your next visit.
            </p>
            <p className="mt-3">
              If you do not want this, you can set up your browser to inform you about the setting 
              of cookies and only allow them in individual cases. Disabling cookies may limit the 
              functionality of this website.
            </p>

            <h3 className="text-lg font-semibold mt-4 mb-2">Server Log Files</h3>
            <p>
              The provider of the pages automatically collects and stores information in so-called 
              server log files, which your browser automatically transmits to us. These are:
            </p>
            <ul className="list-disc ml-6 mt-2">
              <li>Browser type and browser version</li>
              <li>Operating system used</li>
              <li>Referrer URL</li>
              <li>Host name of the accessing computer</li>
              <li>Time of the server request</li>
              <li>IP address</li>
            </ul>
            <p className="mt-3">
              This data is not combined with other data sources. The basis for data processing is 
              Art. 6 (1) (f) GDPR, which allows the processing of data to fulfill a contract or for 
              measures preliminary to a contract.
            </p>

            <h3 className="text-lg font-semibold mt-4 mb-2">Contact Form</h3>
            <p>
              If you send us inquiries via the contact form, your information from the inquiry form, 
              including the contact details you provide there, will be stored by us for the purpose 
              of processing the inquiry and in case of follow-up questions. We do not share this data 
              without your consent.
            </p>
            <p className="mt-3">
              The processing of this data is based on Art. 6 (1) (b) GDPR if your request is related 
              to the execution of a contract or is necessary for the implementation of pre-contractual 
              measures. In all other cases, the processing is based on our legitimate interest in the 
              effective processing of the requests addressed to us (Art. 6 (1) (f) GDPR) or on your 
              agreement (Art. 6 (1) (a) GDPR) if this has been requested.
            </p>
            <p className="mt-3">
              The data you enter in the contact form will remain with us until you request us to 
              delete it, revoke your consent to storage, or the purpose for data storage no longer 
              applies (e.g., after your request has been processed). Mandatory statutory provisions—in 
              particular retention periods—remain unaffected.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">4. Analytics and Third-Party Tools</h2>
            
            <h3 className="text-lg font-semibold mt-4 mb-2">Plausible Analytics</h3>
            <p>
              This website uses Plausible Analytics, a privacy-friendly web analytics service that 
              does not use cookies and is fully compliant with GDPR, CCPA, and PECR. Plausible does 
              not collect any personal data or personally identifiable information (PII), and all 
              data is aggregated. Your IP address is only used to determine your country and is not 
              stored.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">5. Your Rights</h2>
            <p>You have the following rights:</p>
            <ul className="list-disc ml-6 mt-2">
              <li><strong>Right to information:</strong> You can request information about your personal data processed by us.</li>
              <li><strong>Right to correction:</strong> If your data is incorrect or incomplete, you can request correction.</li>
              <li><strong>Right to deletion:</strong> You can request the deletion of your personal data.</li>
              <li><strong>Right to restriction of processing:</strong> You can request that we restrict the processing of your personal data.</li>
              <li><strong>Right to object:</strong> You can object to the processing of your data at any time.</li>
              <li><strong>Right to data portability:</strong> You have the right to have data that we process automatically on the basis of your consent or in fulfillment of a contract handed over to you or to a third party in a common, machine-readable format.</li>
            </ul>
            <p className="mt-3">
              To exercise these rights, please contact us at privacy@greenstemglobal.com.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">6. Data Security</h2>
            <p>
              We use appropriate technical and organizational security measures to protect your data 
              against accidental or intentional manipulation, partial or complete loss, destruction, 
              or unauthorized access by third parties. Our security measures are continuously improved 
              in line with technological development.
            </p>
            <p className="mt-3">
              This website uses SSL or TLS encryption for security reasons and to protect the 
              transmission of confidential content, such as requests that you send to us as the site 
              operator. You can recognize an encrypted connection by the fact that the address line 
              of the browser changes from "http://" to "https://" and by the lock symbol in your 
              browser line.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">7. Changes to This Privacy Policy</h2>
            <p>
              We may update this privacy policy from time to time to reflect changes in our practices 
              or for other operational, legal, or regulatory reasons. We will notify you of any 
              material changes by posting the new privacy policy on this page and updating the "Last 
              updated" date.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">8. Contact Information</h2>
            <p>
              If you have any questions about this privacy policy or our data protection practices, 
              please contact us at:
            </p>
            <p className="mt-3">
              Email: privacy@greenstemglobal.com<br />
              Phone: +49 30 1234 5678<br />
              Address: Friedrichstraße 123, 10117 Berlin, Germany
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}
