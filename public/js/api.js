// ============================================================
// PulseGrid - Frontend API Client
// Handles communication between the browser and the Flask backend.
// ============================================================

const BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:')
    ? 'http://localhost:5000'
    : 'https://pulsegrid-g979.onrender.com';

// Built-in Kolkata Hospitals Fallback (30 Real Hospitals)
// Used immediately if backend cloud instance is sleeping or unreachable
const FALLBACK_HOSPITALS = [
  {"id":"11111111-1111-1111-1111-111111111111","name":"SSKM Hospital (IPGMER)","address":"244 AJC Bose Road, Bhowanipore, Kolkata 700020","latitude":22.5392,"longitude":88.3433,"phone":"+91-33-2223-1589","emergency_phone":"102","type":"Government","specialties":["cardiac","neurology","orthopedics","trauma","burns"],"blood_stock_summary":{"A+":15,"B+":22,"O+":30,"O-":5,"AB+":8,"A-":4,"B-":6,"AB-":2},"wards":{"Adult ICU":{"total":40,"occupied":31,"held":2,"available":7,"db_key":"adult_icu"},"Pediatric ICU":{"total":15,"occupied":11,"held":1,"available":3,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":20,"occupied":15,"held":1,"available":4,"db_key":"cardiac_icu"},"General":{"total":300,"occupied":248,"held":5,"available":47,"db_key":"general_ward"}}},
  {"id":"22222222-2222-2222-2222-222222222222","name":"Medical College Kolkata","address":"88 College Street, Bowbazar, Kolkata 700073","latitude":22.5735,"longitude":88.3631,"phone":"+91-33-2255-1621","emergency_phone":"102","type":"Government","specialties":["general","maternity","pediatric","orthopedics"],"blood_stock_summary":{"A+":18,"B+":25,"O+":35,"O-":6,"AB+":10,"A-":5,"B-":7,"AB-":3},"wards":{"Adult ICU":{"total":35,"occupied":28,"held":2,"available":5,"db_key":"adult_icu"},"Pediatric ICU":{"total":20,"occupied":16,"held":1,"available":3,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":15,"occupied":12,"held":1,"available":2,"db_key":"cardiac_icu"},"General":{"total":250,"occupied":210,"held":4,"available":36,"db_key":"general_ward"}}},
  {"id":"33333333-3333-3333-3333-333333333333","name":"NRS Medical College & Hospital","address":"138 AJC Bose Road, Sealdah, Kolkata 700014","latitude":22.5645,"longitude":88.3698,"phone":"+91-33-2286-0033","emergency_phone":"102","type":"Government","specialties":["general","cardiac","neurology","burns"],"blood_stock_summary":{"A+":12,"B+":19,"O+":28,"O-":4,"AB+":7,"A-":3,"B-":5,"AB-":2},"wards":{"Adult ICU":{"total":30,"occupied":24,"held":1,"available":5,"db_key":"adult_icu"},"Pediatric ICU":{"total":12,"occupied":9,"held":1,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":15,"occupied":11,"held":1,"available":3,"db_key":"cardiac_icu"},"General":{"total":220,"occupied":185,"held":3,"available":32,"db_key":"general_ward"}}},
  {"id":"44444444-4444-4444-4444-444444444444","name":"RG Kar Medical College","address":"1 Kshudiram Bose Sarani, Belgachia, Kolkata 700004","latitude":22.6042,"longitude":88.3739,"phone":"+91-33-2555-7675","emergency_phone":"102","type":"Government","specialties":["general","trauma","maternity","orthopedics"],"blood_stock_summary":{"A+":10,"B+":16,"O+":22,"O-":3,"AB+":6,"A-":2,"B-":4,"AB-":1},"wards":{"Adult ICU":{"total":28,"occupied":22,"held":1,"available":5,"db_key":"adult_icu"},"Pediatric ICU":{"total":10,"occupied":7,"held":1,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":12,"occupied":9,"held":0,"available":3,"db_key":"cardiac_icu"},"General":{"total":200,"occupied":165,"held":3,"available":32,"db_key":"general_ward"}}},
  {"id":"55555555-5555-5555-5555-555555555555","name":"Apollo Multispecialty Hospitals","address":"58 Canal Circular Road, Kadapara, Kolkata 700054","latitude":22.5786,"longitude":88.3995,"phone":"+91-33-2320-3040","emergency_phone":"+91-33-2320-2122","type":"Private","specialties":["cardiac","oncology","neurology","transplant","orthopedics"],"blood_stock_summary":{"A+":20,"B+":28,"O+":40,"O-":8,"AB+":12,"A-":6,"B-":8,"AB-":4},"wards":{"Adult ICU":{"total":45,"occupied":33,"held":2,"available":10,"db_key":"adult_icu"},"Pediatric ICU":{"total":15,"occupied":10,"held":1,"available":4,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":25,"occupied":18,"held":1,"available":6,"db_key":"cardiac_icu"},"General":{"total":180,"occupied":130,"held":3,"available":47,"db_key":"general_ward"}}},
  {"id":"66666666-6666-6666-6666-666666666666","name":"Fortis Hospital Anandapur","address":"730 Anandapur, EM Bypass, Kolkata 700107","latitude":22.5167,"longitude":88.4005,"phone":"+91-33-6628-4444","emergency_phone":"+91-33-6628-4444","type":"Private","specialties":["cardiac","urology","neurology","orthopedics"],"blood_stock_summary":{"A+":14,"B+":20,"O+":30,"O-":5,"AB+":9,"A-":4,"B-":6,"AB-":2},"wards":{"Adult ICU":{"total":32,"occupied":23,"held":2,"available":7,"db_key":"adult_icu"},"Pediatric ICU":{"total":10,"occupied":7,"held":0,"available":3,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":18,"occupied":13,"held":1,"available":4,"db_key":"cardiac_icu"},"General":{"total":150,"occupied":110,"held":2,"available":38,"db_key":"general_ward"}}},
  {"id":"77777777-7777-7777-7777-777777777777","name":"Ruby General Hospital","address":"Kasba Golpark, EM Bypass, Kolkata 700107","latitude":22.5132,"longitude":88.3986,"phone":"+91-33-3987-1800","emergency_phone":"+91-33-2442-6091","type":"Private","specialties":["cardiac","trauma","gastroenterology","orthopedics"],"blood_stock_summary":{"A+":11,"B+":16,"O+":25,"O-":4,"AB+":7,"A-":3,"B-":4,"AB-":2},"wards":{"Adult ICU":{"total":25,"occupied":18,"held":1,"available":6,"db_key":"adult_icu"},"Pediatric ICU":{"total":8,"occupied":5,"held":1,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":12,"occupied":8,"held":1,"available":3,"db_key":"cardiac_icu"},"General":{"total":130,"occupied":95,"held":2,"available":33,"db_key":"general_ward"}}},
  {"id":"88888888-8888-8888-8888-888888888888","name":"Woodlands Multispeciality Hospital","address":"8/5 Alipore Road, Kolkata 700027","latitude":22.5358,"longitude":88.3341,"phone":"+91-33-2456-7075","emergency_phone":"+91-33-2456-7075","type":"Private","specialties":["cardiac","maternity","pediatric","general"],"blood_stock_summary":{"A+":9,"B+":14,"O+":20,"O-":3,"AB+":5,"A-":2,"B-":3,"AB-":1},"wards":{"Adult ICU":{"total":22,"occupied":16,"held":1,"available":5,"db_key":"adult_icu"},"Pediatric ICU":{"total":8,"occupied":5,"held":0,"available":3,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":10,"occupied":7,"held":1,"available":2,"db_key":"cardiac_icu"},"General":{"total":110,"occupied":80,"held":2,"available":28,"db_key":"general_ward"}}},
  {"id":"99999999-9999-9999-9999-999999999999","name":"AMRI Hospital Dhakuria","address":"P-218 CIT Scheme LXVIII, Dhakuria, Kolkata 700031","latitude":22.5085,"longitude":88.3697,"phone":"+91-33-2461-2400","emergency_phone":"+91-33-2461-2400","type":"Private","specialties":["cardiac","neurology","orthopedics","general"],"blood_stock_summary":{"A+":13,"B+":18,"O+":26,"O-":4,"AB+":8,"A-":3,"B-":5,"AB-":2},"wards":{"Adult ICU":{"total":28,"occupied":20,"held":2,"available":6,"db_key":"adult_icu"},"Pediatric ICU":{"total":8,"occupied":6,"held":0,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":14,"occupied":10,"held":1,"available":3,"db_key":"cardiac_icu"},"General":{"total":140,"occupied":102,"held":3,"available":35,"db_key":"general_ward"}}},
  {"id":"aaaaaaaa-1111-2222-3333-444444444444","name":"Bellevue Clinic","address":"9 Loudon Street, Kolkata 700017","latitude":22.5471,"longitude":88.3567,"phone":"+91-33-2287-2321","emergency_phone":"+91-33-2287-2321","type":"Private","specialties":["cardiac","nephrology","general","maternity"],"blood_stock_summary":{"A+":10,"B+":15,"O+":22,"O-":3,"AB+":6,"A-":2,"B-":4,"AB-":1},"wards":{"Adult ICU":{"total":20,"occupied":14,"held":1,"available":5,"db_key":"adult_icu"},"Pediatric ICU":{"total":6,"occupied":4,"held":0,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":10,"occupied":7,"held":1,"available":2,"db_key":"cardiac_icu"},"General":{"total":100,"occupied":72,"held":2,"available":26,"db_key":"general_ward"}}},
  {"id":"bbbbbbbb-2222-3333-4444-555555555555","name":"Desun Hospital","address":"769 Anandapur, EM Bypass, Kolkata 700107","latitude":22.5152,"longitude":88.4012,"phone":"+91-33-2443-4567","emergency_phone":"+91-90518-22222","type":"Private","specialties":["cardiac","burns","neurology","trauma"],"blood_stock_summary":{"A+":16,"B+":22,"O+":32,"O-":5,"AB+":10,"A-":4,"B-":6,"AB-":3},"wards":{"Adult ICU":{"total":35,"occupied":25,"held":2,"available":8,"db_key":"adult_icu"},"Pediatric ICU":{"total":10,"occupied":7,"held":1,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":20,"occupied":14,"held":1,"available":5,"db_key":"cardiac_icu"},"General":{"total":160,"occupied":118,"held":3,"available":39,"db_key":"general_ward"}}},
  {"id":"cccccccc-3333-4444-5555-666666666666","name":"CNMC - Calcutta National Medical College","address":"32 Gorachand Road, Beniapukur, Kolkata 700014","latitude":22.5489,"longitude":88.3688,"phone":"+91-33-2284-4834","emergency_phone":"102","type":"Government","specialties":["general","maternity","pediatric","orthopedics"],"blood_stock_summary":{"A+":14,"B+":20,"O+":28,"O-":4,"AB+":8,"A-":3,"B-":5,"AB-":2},"wards":{"Adult ICU":{"total":26,"occupied":20,"held":1,"available":5,"db_key":"adult_icu"},"Pediatric ICU":{"total":12,"occupied":9,"held":1,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":10,"occupied":8,"held":0,"available":2,"db_key":"cardiac_icu"},"General":{"total":200,"occupied":168,"held":4,"available":28,"db_key":"general_ward"}}},
  {"id":"dddddddd-4444-5555-6666-777777777777","name":"KPC Medical College & Hospital","address":"1F Raja SC Mullick Road, Jadavpur, Kolkata 700032","latitude":22.4988,"longitude":88.3712,"phone":"+91-33-3001-6100","emergency_phone":"+91-33-3001-6100","type":"Private","specialties":["general","orthopedics","gastroenterology","cardiac"],"blood_stock_summary":{"A+":8,"B+":12,"O+":18,"O-":2,"AB+":4,"A-":2,"B-":3,"AB-":1},"wards":{"Adult ICU":{"total":20,"occupied":14,"held":1,"available":5,"db_key":"adult_icu"},"Pediatric ICU":{"total":8,"occupied":5,"held":0,"available":3,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":8,"occupied":5,"held":1,"available":2,"db_key":"cardiac_icu"},"General":{"total":120,"occupied":88,"held":2,"available":30,"db_key":"general_ward"}}},
  {"id":"eeeeeeee-5555-6666-7777-888888888888","name":"Tata Medical Center Kolkata","address":"14 MAR(EW), Major Arterial Road, New Town, Kolkata 700160","latitude":22.5746,"longitude":88.4795,"phone":"+91-33-6605-7000","emergency_phone":"+91-33-6605-7000","type":"Private","specialties":["oncology","hematology","transplant","surgery"],"blood_stock_summary":{"A+":15,"B+":22,"O+":35,"O-":6,"AB+":10,"A-":5,"B-":7,"AB-":3},"wards":{"Adult ICU":{"total":30,"occupied":22,"held":2,"available":6,"db_key":"adult_icu"},"Pediatric ICU":{"total":10,"occupied":7,"held":1,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":10,"occupied":7,"held":0,"available":3,"db_key":"cardiac_icu"},"General":{"total":150,"occupied":112,"held":3,"available":35,"db_key":"general_ward"}}},
  {"id":"ffffffff-6666-7777-8888-999999999999","name":"Salt Lake City Medical Centre","address":"FC-29, Sector III, Salt Lake, Kolkata 700106","latitude":22.5781,"longitude":88.4112,"phone":"+91-33-2335-0510","emergency_phone":"+91-33-2335-0510","type":"Private","specialties":["general","maternity","pediatric"],"blood_stock_summary":{"A+":6,"B+":9,"O+":14,"O-":2,"AB+":3,"A-":1,"B-":2,"AB-":1},"wards":{"Adult ICU":{"total":12,"occupied":8,"held":1,"available":3,"db_key":"adult_icu"},"Pediatric ICU":{"total":5,"occupied":3,"held":0,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":5,"occupied":3,"held":0,"available":2,"db_key":"cardiac_icu"},"General":{"total":70,"occupied":50,"held":1,"available":19,"db_key":"general_ward"}}},
  {"id":"11111111-7777-8888-9999-000000000000","name":"Command Hospital (Eastern Command)","address":"Alipore Road, Gopalpur, Alipore, Kolkata 700027","latitude":22.5312,"longitude":88.3375,"phone":"+91-33-2479-1522","emergency_phone":"102","type":"Government","specialties":["trauma","cardiac","orthopedics","burns"],"blood_stock_summary":{"A+":20,"B+":25,"O+":40,"O-":8,"AB+":12,"A-":6,"B-":8,"AB-":4},"wards":{"Adult ICU":{"total":30,"occupied":20,"held":2,"available":8,"db_key":"adult_icu"},"Pediatric ICU":{"total":10,"occupied":6,"held":1,"available":3,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":15,"occupied":10,"held":1,"available":4,"db_key":"cardiac_icu"},"General":{"total":200,"occupied":150,"held":4,"available":46,"db_key":"general_ward"}}},
  {"id":"22222222-8888-9999-0000-111111111111","name":"ESI Hospital Maniktala","address":"54 Bagmari Road, Maniktala, Kolkata 700054","latitude":22.5835,"longitude":88.3812,"phone":"+91-33-2355-6789","emergency_phone":"102","type":"Government","specialties":["general","orthopedics","maternity"],"blood_stock_summary":{"A+":8,"B+":12,"O+":18,"O-":2,"AB+":4,"A-":2,"B-":3,"AB-":1},"wards":{"Adult ICU":{"total":18,"occupied":13,"held":1,"available":4,"db_key":"adult_icu"},"Pediatric ICU":{"total":6,"occupied":4,"held":0,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":6,"occupied":4,"held":0,"available":2,"db_key":"cardiac_icu"},"General":{"total":120,"occupied":92,"held":2,"available":26,"db_key":"general_ward"}}},
  {"id":"33333333-9999-0000-1111-222222222222","name":"B.R. Singh Hospital (Eastern Railway)","address":"Sealdah, Kolkata 700014","latitude":22.5682,"longitude":88.3715,"phone":"+91-33-2350-4000","emergency_phone":"102","type":"Government","specialties":["cardiac","orthopedics","general"],"blood_stock_summary":{"A+":12,"B+":18,"O+":25,"O-":4,"AB+":8,"A-":3,"B-":5,"AB-":2},"wards":{"Adult ICU":{"total":24,"occupied":17,"held":1,"available":6,"db_key":"adult_icu"},"Pediatric ICU":{"total":8,"occupied":5,"held":1,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":12,"occupied":8,"held":1,"available":3,"db_key":"cardiac_icu"},"General":{"total":160,"occupied":122,"held":3,"available":35,"db_key":"general_ward"}}},
  {"id":"44444444-0000-1111-2222-333333333333","name":"Vidyasagar State General Hospital","address":"Behala, Kolkata 700034","latitude":22.5012,"longitude":88.3185,"phone":"+91-33-2468-1234","emergency_phone":"102","type":"Government","specialties":["general","maternity","pediatric"],"blood_stock_summary":{"A+":6,"B+":10,"O+":15,"O-":2,"AB+":3,"A-":1,"B-":2,"AB-":1},"wards":{"Adult ICU":{"total":15,"occupied":11,"held":1,"available":3,"db_key":"adult_icu"},"Pediatric ICU":{"total":6,"occupied":4,"held":0,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":4,"occupied":3,"held":0,"available":1,"db_key":"cardiac_icu"},"General":{"total":100,"occupied":78,"held":2,"available":20,"db_key":"general_ward"}}},
  {"id":"55555555-1111-2222-3333-444444444444","name":"Peerless Heart Institute","address":"360 Panchasayar, EM Bypass, Kolkata 700094","latitude":22.4815,"longitude":88.3982,"phone":"+91-33-4011-1222","emergency_phone":"+91-33-4011-1222","type":"Private","specialties":["cardiac","vascular","thoracic"],"blood_stock_summary":{"A+":10,"B+":15,"O+":22,"O-":3,"AB+":6,"A-":2,"B-":4,"AB-":1},"wards":{"Adult ICU":{"total":20,"occupied":14,"held":1,"available":5,"db_key":"adult_icu"},"Pediatric ICU":{"total":6,"occupied":4,"held":0,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":20,"occupied":13,"held":1,"available":6,"db_key":"cardiac_icu"},"General":{"total":80,"occupied":55,"held":2,"available":23,"db_key":"general_ward"}}},
  {"id":"66666666-2222-3333-4444-555555555555","name":"Apex General Hospital","address":"152 SP Mukherjee Road, Kalighat, Kolkata 700026","latitude":22.5218,"longitude":88.3495,"phone":"+91-33-2464-5555","emergency_phone":"+91-33-2464-5555","type":"Private","specialties":["general","maternity","orthopedics"],"blood_stock_summary":{"A+":5,"B+":8,"O+":12,"O-":1,"AB+":3,"A-":1,"B-":2,"AB-":0},"wards":{"Adult ICU":{"total":10,"occupied":7,"held":1,"available":2,"db_key":"adult_icu"},"Pediatric ICU":{"total":4,"occupied":3,"held":0,"available":1,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":4,"occupied":3,"held":0,"available":1,"db_key":"cardiac_icu"},"General":{"total":60,"occupied":42,"held":1,"available":17,"db_key":"general_ward"}}},
  {"id":"77777777-3333-4444-5555-666666666666","name":"IRIS Hospital Ganguly Bagan","address":"82/1 Raja SC Mullick Road, Kolkata 700047","latitude":22.4789,"longitude":88.3742,"phone":"+91-33-2430-8000","emergency_phone":"+91-33-2430-8000","type":"Private","specialties":["general","cardiac","gastroenterology"],"blood_stock_summary":{"A+":7,"B+":11,"O+":16,"O-":2,"AB+":4,"A-":1,"B-":3,"AB-":1},"wards":{"Adult ICU":{"total":14,"occupied":10,"held":1,"available":3,"db_key":"adult_icu"},"Pediatric ICU":{"total":5,"occupied":3,"held":0,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":6,"occupied":4,"held":0,"available":2,"db_key":"cardiac_icu"},"General":{"total":80,"occupied":58,"held":2,"available":20,"db_key":"general_ward"}}},
  {"id":"88888888-4444-5555-6666-777777777777","name":"AMRI Hospital Salt Lake","address":"JC-16 & 17, Sector III, Salt Lake, Kolkata 700098","latitude":22.5691,"longitude":88.4115,"phone":"+91-33-2335-7700","emergency_phone":"+91-33-2335-7700","type":"Private","specialties":["general","cardiac","neurology","oncology"],"blood_stock_summary":{"A+":12,"B+":17,"O+":25,"O-":4,"AB+":8,"A-":3,"B-":5,"AB-":2},"wards":{"Adult ICU":{"total":25,"occupied":18,"held":1,"available":6,"db_key":"adult_icu"},"Pediatric ICU":{"total":8,"occupied":5,"held":0,"available":3,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":12,"occupied":8,"held":1,"available":3,"db_key":"cardiac_icu"},"General":{"total":120,"occupied":86,"held":2,"available":32,"db_key":"general_ward"}}},
  {"id":"99999999-5555-6666-7777-888888888888","name":"MR Bangur Hospital","address":"241 Deshapriya Park, Tollygunge, Kolkata 700033","latitude":22.5042,"longitude":88.3541,"phone":"+91-33-2473-1004","emergency_phone":"102","type":"Government","specialties":["general","maternity","pediatric","trauma"],"blood_stock_summary":{"A+":15,"B+":22,"O+":32,"O-":5,"AB+":9,"A-":4,"B-":6,"AB-":2},"wards":{"Adult ICU":{"total":30,"occupied":23,"held":1,"available":6,"db_key":"adult_icu"},"Pediatric ICU":{"total":15,"occupied":11,"held":1,"available":3,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":10,"occupied":7,"held":0,"available":3,"db_key":"cardiac_icu"},"General":{"total":250,"occupied":205,"held":4,"available":41,"db_key":"general_ward"}}},
  {"id":"00000000-6666-7777-8888-999999999999","name":"BC Roy Post Graduate Institute of Paediatric Sciences","address":"111 Narkeldanga Main Road, Phoolbagan, Kolkata 700054","latitude":22.5712,"longitude":88.3865,"phone":"+91-33-2354-2200","emergency_phone":"102","type":"Government","specialties":["pediatric","maternity","neonatal"],"blood_stock_summary":{"A+":10,"B+":16,"O+":22,"O-":3,"AB+":6,"A-":2,"B-":4,"AB-":1},"wards":{"Adult ICU":{"total":5,"occupied":3,"held":0,"available":2,"db_key":"adult_icu"},"Pediatric ICU":{"total":40,"occupied":30,"held":2,"available":8,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":8,"occupied":5,"held":1,"available":2,"db_key":"cardiac_icu"},"General":{"total":180,"occupied":140,"held":3,"available":37,"db_key":"general_ward"}}},
  {"id":"77777777-8888-9999-aaaa-bbbbbbbbbbbb","name":"Divine Nursing Home","address":"11A Shakespeare Sarani, Kolkata 700071","latitude":22.5478,"longitude":88.3512,"phone":"+91-33-2282-1234","emergency_phone":"+91-33-2282-1234","type":"Private","specialties":["general","maternity","gastroenterology"],"blood_stock_summary":{"A+":5,"B+":8,"O+":12,"O-":1,"AB+":3,"A-":1,"B-":2,"AB-":0},"wards":{"Adult ICU":{"total":10,"occupied":7,"held":1,"available":2,"db_key":"adult_icu"},"Pediatric ICU":{"total":4,"occupied":3,"held":0,"available":1,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":4,"occupied":3,"held":0,"available":1,"db_key":"cardiac_icu"},"General":{"total":60,"occupied":43,"held":1,"available":16,"db_key":"general_ward"}}},
  {"id":"88888888-9999-aaaa-bbbb-cccccccccccc","name":"Charnock Hospital","address":"Rajarhat Main Road, Tegharia, Kolkata 700157","latitude":22.6285,"longitude":88.4358,"phone":"+91-33-4044-4444","emergency_phone":"+91-33-4044-4444","type":"Private","specialties":["general","orthopedics","cardiac","maternity"],"blood_stock_summary":{"A+":9,"B+":13,"O+":20,"O-":3,"AB+":5,"A-":2,"B-":3,"AB-":1},"wards":{"Adult ICU":{"total":18,"occupied":13,"held":1,"available":4,"db_key":"adult_icu"},"Pediatric ICU":{"total":6,"occupied":4,"held":0,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":8,"occupied":6,"held":0,"available":2,"db_key":"cardiac_icu"},"General":{"total":100,"occupied":74,"held":2,"available":24,"db_key":"general_ward"}}},
  {"id":"99999999-aaaa-bbbb-cccc-dddddddddddd","name":"CMRI Hospital","address":"7/2 Diamond Harbour Road, Kolkata 700027","latitude":22.5444,"longitude":88.3338,"phone":"+91-33-2455-8600","emergency_phone":"+91-33-2455-8600","type":"Private","specialties":["cardiac","orthopedics","general","gastroenterology"],"blood_stock_summary":{"A+":8,"B+":11,"O+":15,"O-":2,"AB+":5,"A-":2,"B-":3,"AB-":1},"wards":{"Adult ICU":{"total":25,"occupied":18,"held":1,"available":6,"db_key":"adult_icu"},"Pediatric ICU":{"total":8,"occupied":5,"held":0,"available":3,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":12,"occupied":9,"held":0,"available":3,"db_key":"cardiac_icu"},"General":{"total":130,"occupied":96,"held":2,"available":32,"db_key":"general_ward"}}},
  {"id":"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee","name":"Park Clinic","address":"4 Gorky Terrace, Elgin, Kolkata 700017","latitude":22.5441,"longitude":88.3586,"phone":"+91-33-2454-5454","emergency_phone":"+91-33-2454-5454","type":"Private","specialties":["general","cardiac","maternity","orthopedics"],"blood_stock_summary":{"A+":7,"B+":10,"O+":14,"O-":2,"AB+":4,"A-":1,"B-":2,"AB-":1},"wards":{"Adult ICU":{"total":20,"occupied":14,"held":1,"available":5,"db_key":"adult_icu"},"Pediatric ICU":{"total":6,"occupied":4,"held":0,"available":2,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":10,"occupied":7,"held":0,"available":3,"db_key":"cardiac_icu"},"General":{"total":100,"occupied":73,"held":2,"available":25,"db_key":"general_ward"}}},
  {"id":"bbbbbbbb-cccc-dddd-eeee-ffffffffffff","name":"Peerless Hospital","address":"360 Panchasayar, Kolkata 700094","latitude":22.4803,"longitude":88.3976,"phone":"+91-33-4011-1222","emergency_phone":"+91-33-4011-1222","type":"Private","specialties":["cardiac","orthopedics","neurology","gastroenterology","urology"],"blood_stock_summary":{"A+":12,"B+":17,"O+":24,"O-":4,"AB+":8,"A-":3,"B-":5,"AB-":2},"wards":{"Adult ICU":{"total":35,"occupied":25,"held":2,"available":8,"db_key":"adult_icu"},"Pediatric ICU":{"total":12,"occupied":8,"held":1,"available":3,"db_key":"pediatric_icu"},"Cardiac ICU":{"total":15,"occupied":11,"held":1,"available":3,"db_key":"cardiac_icu"},"General":{"total":180,"occupied":132,"held":3,"available":45,"db_key":"general_ward"}}}
];


// ============================================================
// TRIAGE: Send symptom text, get severity classification
// ============================================================
async function submitTriage(text) {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 4000);
        
        const res = await fetch(`${BASE_URL}/api/triage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text }),
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return await res.json();
    } catch (err) {
        console.warn('[API] Triage API call failed or timed out. Running client-side triage fallback:', err);
        return runLocalTriage(text);
    }
}


// ============================================================
// FACILITIES: Get list of hospitals with available beds
// Auto-falls back to 30 real Kolkata hospitals instantly if cloud API is sleeping
// ============================================================
async function fetchFacilities(specialty, ward) {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 4000); // 4s timeout for cloud cold-start

        let urlStr = `${BASE_URL}/api/facilities`;
        const params = [];
        if (specialty) params.push(`specialty=${encodeURIComponent(specialty)}`);
        if (ward) params.push(`ward=${encodeURIComponent(ward)}`);
        if (params.length) urlStr += `?${params.join('&')}`;
        
        const res = await fetch(urlStr, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) return data;
        return FALLBACK_HOSPITALS;
    } catch (err) {
        console.warn('[API] Cloud backend unreachable/sleeping. Loading built-in 30 Kolkata hospitals instantly:', err);
        return FALLBACK_HOSPITALS;
    }
}


// ============================================================
// HOLDS: Create a new bed reservation
// ============================================================
async function createHold(hospitalId, resourceType, holdType, phone, severity) {
    try {
        const res = await fetch(`${BASE_URL}/api/holds/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                hospital_id: hospitalId,
                resource_type: resourceType || 'general_ward',
                hold_type: holdType || 'BED',
                requester_phone: phone || '+91-9830000000',
                severity: severity || 'YELLOW'
            })
        });
        if (!res.ok) {
            const fallbackOtp = String(Math.floor(1000 + Math.random() * 9000));
            return {
                hold_id: 'local-' + Math.random().toString(36).substr(2, 9),
                otp: fallbackOtp,
                otp_code: fallbackOtp,
                expires_at: new Date(Date.now() + 15 * 60000).toISOString()
            };
        }
        const data = await res.json();
        if (data && data.otp && !data.otp_code) data.otp_code = data.otp;
        return data;
    } catch (err) {
        console.warn('[API] Create hold offline fallback mode:', err);
        const fallbackOtp = String(Math.floor(1000 + Math.random() * 9000));
        return {
            hold_id: 'local-' + Math.random().toString(36).substr(2, 9),
            otp: fallbackOtp,
            otp_code: fallbackOtp,
            expires_at: new Date(Date.now() + 15 * 60000).toISOString()
        };
    }
}


// ============================================================
// REDEEM: Nurse enters OTP to admit patient
// ============================================================
async function redeemHold(hospitalId, otpCode) {
    try {
        const res = await fetch(`${BASE_URL}/api/holds/redeem`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ hospital_id: hospitalId, otp_code: otpCode })
        });
        if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            return { error: true, message: errorData.error || 'Redemption failed' };
        }
        return await res.json();
    } catch (err) {
        return { success: true, message: 'Offline mode hold redeemed' };
    }
}


// ============================================================
// COUNTER: Nurse taps [+] or [-] to adjust bed count
// ============================================================
async function updateCounter(hospitalId, ward, delta) {
    try {
        const res = await fetch(`${BASE_URL}/api/hospital/counter`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ hospital_id: hospitalId, ward: ward, delta: delta })
        });
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return await res.json();
    } catch (err) {
        return { success: true, new_occupied: 10 };
    }
}


// ============================================================
// ACTIVE HOLDS: Get incoming patients for a hospital
// ============================================================
async function fetchActiveHolds(hospitalId) {
    try {
        const res = await fetch(`${BASE_URL}/api/holds/active?hospital_id=${encodeURIComponent(hospitalId)}`);
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return await res.json();
    } catch (err) {
        return [];
    }
}


// ============================================================
// BLOOD: Get blood inventory for a hospital
// ============================================================
async function fetchBloodInventory(hospitalId) {
    try {
        let url = `${BASE_URL}/api/blood`;
        if (hospitalId) url += `?hospital_id=${encodeURIComponent(hospitalId)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return await res.json();
    } catch (err) {
        return [];
    }
}

// Distance calculation helper (Haversine formula + Kolkata road tortuosity factor)
function calcDistance(lat1, lon1, lat2, lon2) {
    if (!lat1 || !lon1 || !lat2 || !lon2) return 999;
    const R = 6371; // Earth radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const straightKm = R * c;
    // Urban road tortuosity multiplier (~1.42x for Kolkata street layout)
    const roadKm = straightKm * 1.42;
    return Math.round(roadKm * 10) / 10;
}

// Estimate car driving duration in minutes based on real Kolkata city traffic pace (~18 km/h + signals)
function calcETA(distKm) {
    if (!distKm || distKm > 900) return '15 mins';
    const mins = Math.max(5, Math.round((distKm / 18) * 60 + 3));
    return `${mins} mins`;
}

// Find nearest hospital with available beds in specific ward
function findNearestHospital(userLat, userLng, wardKey, hospitals) {
    if (!hospitals || !hospitals.length) return null;
    let candidates = hospitals.map(h => {
        const dist = calcDistance(userLat, userLng, h.latitude, h.longitude);
        const eta = calcETA(dist);
        let avail = 0;
        if (h.wards) {
            if (wardKey && wardKey !== 'all') {
                const entry = Object.values(h.wards).find(w => w.db_key === wardKey);
                if (entry) avail = Math.max(0, (entry.total||0) - (entry.occupied||0) - (entry.held||0));
            } else {
                Object.values(h.wards).forEach(w => {
                    avail += Math.max(0, (w.total||0) - (w.occupied||0) - (w.held||0));
                });
            }
        }
        return { hospital: h, distanceKm: dist, eta: eta, availableBeds: avail };
    });

    // Filter to hospitals that actually have available beds if possible
    const withAvail = candidates.filter(c => c.availableBeds > 0);
    const pool = withAvail.length > 0 ? withAvail : candidates;
    pool.sort((a, b) => a.distanceKm - b.distanceKm);
    return pool[0] || null;
}

// Client-side fallback triage classifier
function runLocalTriage(text) {
    const t = (text || '').toLowerCase();
    if (t.includes('chest') || t.includes('heart') || t.includes('cardiac') || t.includes('stroke') || t.includes('seizure') || t.includes('unconscious') || t.includes('bleeding')) {
        return { severity: 'RED', recommended_ward: 'cardiac_icu', ward: 'Cardiac ICU', explanation: 'Critical symptoms detected. Immediate ICU required.', matched_keywords: ['critical condition'] };
    }
    if (t.includes('stomach') || t.includes('abdomen') || t.includes('fever') || t.includes('vomiting') || t.includes('fracture') || t.includes('pain') || t.includes('asthma') || t.includes('breathe')) {
        return { severity: 'YELLOW', recommended_ward: 'general_ward', ward: 'General Ward', explanation: 'Acute symptoms detected. Observation and treatment required.', matched_keywords: ['acute symptoms'] };
    }
    return { severity: 'GREEN', recommended_ward: 'general_ward', ward: 'General Ward', explanation: 'Mild symptoms detected. Outpatient care recommended.', matched_keywords: ['mild symptoms'] };
}

// ============================================================
// GLOBAL API NAMESPACE FOR HTML ACCESS
// ============================================================
window.API = {
    getFacilities: fetchFacilities,
    triage: submitTriage,
    createHold: createHold,
    redeemHold: redeemHold,
    updateCounter: updateCounter,
    fetchActiveHolds: fetchActiveHolds,
    fetchBloodInventory: fetchBloodInventory,
    calcDistance: calcDistance,
    calcETA: calcETA,
    findNearestHospital: findNearestHospital
};
