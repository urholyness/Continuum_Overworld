export const metadata = {
  title: 'Imprint',
  description: 'Legal information and imprint for GreenStemGlobal.',
}

export default function ImprintPage() {
  return (
    <div className="py-20 bg-white">
      <div className="container">
        <div className="max-w-3xl mx-auto prose prose-lg">
          <h1 className="text-3xl font-display font-bold mb-8">Imprint</h1>
          
          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Information according to § 5 TMG</h2>
            <p>
              GreenStemGlobal GmbH<br />
              Friedrichstraße 123<br />
              10117 Berlin<br />
              Germany
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Represented by</h2>
            <p>Managing Directors: [To be provided]</p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Contact</h2>
            <p>
              Phone: +49 30 1234 5678<br />
              Email: info@greenstemglobal.com
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Register Entry</h2>
            <p>
              Entry in the Commercial Register<br />
              Register Court: Amtsgericht Charlottenburg (Berlin)<br />
              Register Number: HRB [To be provided]
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">VAT ID</h2>
            <p>
              VAT identification number according to § 27a UStG:<br />
              DE [To be provided]
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Responsible for Content</h2>
            <p>
              According to § 55 Abs. 2 RStV:<br />
              [To be provided]<br />
              Friedrichstraße 123<br />
              10117 Berlin
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Disclaimer</h2>
            
            <h3 className="text-lg font-semibold mt-4 mb-2">Liability for Content</h3>
            <p>
              The contents of our pages have been created with the utmost care. However, we cannot 
              guarantee the contents' accuracy, completeness, or topicality. According to statutory 
              provisions, we are furthermore responsible for our own content on these web pages. 
              In this matter, please note that we are not obliged to monitor the transmitted or 
              saved information of third parties, or investigate circumstances pointing to illegal 
              activity.
            </p>

            <h3 className="text-lg font-semibold mt-4 mb-2">Liability for Links</h3>
            <p>
              Our offer contains links to external third-party websites, over whose contents we have 
              no influence. Therefore, we cannot assume any liability for these external contents. 
              The respective provider or operator of the pages is always responsible for the contents 
              of the linked pages. The linked pages were checked for possible legal violations at the 
              time of linking. Illegal contents were not discernible at the time of linking.
            </p>

            <h3 className="text-lg font-semibold mt-4 mb-2">Copyright</h3>
            <p>
              The content and works on these pages created by the site operators are subject to German 
              copyright law. The reproduction, editing, distribution, and any kind of exploitation 
              outside the limits of copyright require the written consent of the respective author or 
              creator. Downloads and copies of this site are only permitted for private, non-commercial 
              use.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Dispute Resolution</h2>
            <p>
              The European Commission provides a platform for online dispute resolution (ODR):<br />
              <a href="https://ec.europa.eu/consumers/odr/" className="text-leaf hover:underline">
                https://ec.europa.eu/consumers/odr/
              </a><br />
              Our email address can be found above in the imprint.
            </p>
            <p className="mt-2">
              We are not willing or obliged to participate in dispute resolution proceedings before a 
              consumer arbitration board.
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}
