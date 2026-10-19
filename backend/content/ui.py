"""Fixed interface strings (labels/buttons). Editable content lives in the database."""
UI = {
    'en': dict(nav=['Home', 'Our treatments', 'Our prices', 'Offers'], titles={'index': 'Home', 'services': 'Our treatments', 'prices': 'Our prices'},
               desc='Infinite Care Beauty Clinic – The Beauty of Health.',
               form=['Name', 'E-mail', 'Phone (optional)', 'Message', 'Send'],
               ok='Thank you! Your message has been sent – we will get back to you soon.',
               err='Sorry, something went wrong. Please try again or call us.', sending='Sending…',
               inv='Please fill in your name, a valid e-mail address and your message.',
               hours='Open hours:', res='Reservation:', book='Book an appointment', details='Details →',
               pk_h='Our most popular packages', pk_w='package', cur='HUF', offers='Offers', menu='Menu'),
    'hu': dict(nav=['Főoldal', 'Szolgáltatásaink', 'Áraink', 'Akciók'], titles={'index': 'Főoldal', 'services': 'Szolgáltatásaink', 'prices': 'Áraink'},
               desc='Infinite Care Beauty Clinic – Az Egészség Szépsége.',
               form=['Név', 'E-mail', 'Telefon (nem kötelező)', 'Üzenet', 'Elküldöm az üzenetet'],
               ok='Köszönjük! Üzenetedet megkaptuk, hamarosan felvesszük veled a kapcsolatot.',
               err='Hiba történt az elküldés során. Kérjük, próbáld újra, vagy hívj minket.', sending='Küldés…',
               inv='Kérjük, add meg a neved, egy érvényes e-mail címet és az üzeneted.',
               hours='Nyitva:', res='Foglalás:', book='Foglalás', details='Részletek →',
               pk_h='A legnépszerűbb csomagjaink', pk_w='csomag', cur='Ft', offers='Akciók', menu='Menü'),
}
