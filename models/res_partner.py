import requests
import re
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    objective = fields.Text(string="วัตถุประสงค์")
    registration_date = fields.Date(string="วันที่จดทะเบียน")
    business_type_name = fields.Char(string="ประเภทธุรกิจ")

    def action_get_dbd_data(self):
        self.ensure_one()
        
        raw_search = self.vat or self.name
        if not raw_search:
            raise UserError(_("กรุณาระบุเลขนิติบุคคล 13 หลักในช่องชื่อบริษัท หรือช่องเลขผู้เสียภาษี"))
        
        clean_vat = re.sub(r'\D', '', str(raw_search))
        
        if len(clean_vat) != 13:
            raise UserError(_("เลขนิติบุคคลต้องเป็นตัวเลข 13 หลักเท่านั้น (ค่าที่พบ: %s)") % clean_vat)

        get_param = self.env['ir.config_parameter'].sudo().get_param
        api_url = get_param('om_dbd_search.api_url')
        resource_id = get_param('om_dbd_search.resource_id')
        api_token = get_param('om_dbd_search.api_token')

        if not api_url:
            raise UserError("ไม่พบ URL ในการตั้งค่า กรุณาระบุ Endpoint URL ในหน้า Settings ก่อนใช้งาน")

        params = {
            'resource_id': resource_id,
            'q': clean_vat,
            'limit': 1
        }
        
        headers = {}
        if api_token:
            headers['Authorization'] = api_token

        try:
            response = requests.get(api_url, params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                res_json = response.json()
                records = res_json.get('result', {}).get('records', [])

                if not records:
                    raise UserError(_("ไม่พบข้อมูลนิติบุคคลเลขที่ %s ในฐานข้อมูล DBD") % clean_vat)

                data = records[0]
                
                raw_state = data.get('จังหวัด', '').replace('จังหวัด', '').strip()
                
                province_mapping = {
                    'กรุงเทพมหานคร': 'Bangkok',
                    'กระบี่': 'Krabi',
                    'กาญจนบุรี': 'Kanchanaburi',
                    'กาฬสินธุ์': 'Kalasin',
                    'กำแพงเพชร': 'Kamphaeng Phet',
                    'ขอนแก่น': 'Khon Kaen',
                    'จันทบุรี': 'Chanthaburi',
                    'ฉะเชิงเทรา': 'Chachoengsao',
                    'ชลบุรี': 'Chon Buri',
                    'ชัยนาท': 'Chai Nat',
                    'ชัยภูมิ': 'Chaiyaphum',
                    'ชุมพร': 'Chumphon',
                    'เชียงราย': 'Chiang Rai',
                    'เชียงใหม่': 'Chiang Mai',
                    'ตรัง': 'Trang',
                    'ตราด': 'Trat',
                    'ตาก': 'Tak',
                    'นครนายก': 'Nakhon Nayok',
                    'นครปฐม': 'Nakhon Pathom',
                    'นครพนม': 'Nakhon Phanom',
                    'นครราชสีมา': 'Nakhon Ratchasima',
                    'นครศรีธรรมราช': 'Nakhon Si Thammarat',
                    'นครสวรรค์': 'Nakhon Sawan',
                    'นนทบุรี': 'Nonthaburi',
                    'นราธิวาส': 'Narathiwat',
                    'น่าน': 'Nan',
                    'บึงกาฬ': 'Bueng Kan',
                    'บุรีรัมย์': 'Buri Ram',
                    'ปทุมธานี': 'Pathum Thani',
                    'ประจวบคีรีขันธ์': 'Prachuap Khiri Khan',
                    'ปราจีนบุรี': 'Prachin Buri',
                    'ปัตตานี': 'Pattani',
                    'พระนครศรีอยุธยา': 'Phra Nakhon Si Ayutthaya',
                    'พะเยา': 'Phayao',
                    'พังงา': 'Phang Nga',
                    'พัทลุง': 'Phatthalung',
                    'พิจิตร': 'Phichit',
                    'พิษณุโลก': 'Phitsanulok',
                    'เพชรบุรี': 'Phetchaburi',
                    'เพชรบูรณ์': 'Phetchabun',
                    'แพร่': 'Phrae',
                    'ภูเก็ต': 'Phuket',
                    'มหาสารคาม': 'Maha Sarakham',
                    'มุกดาหาร': 'Mukdahan',
                    'แม่ฮ่องสอน': 'Mae Hong Son',
                    'ยโสธร': 'Yasothon',
                    'ยะลา': 'Yala',
                    'ร้อยเอ็ด': 'Roi Et',
                    'ระนอง': 'Ranong',
                    'ระยอง': 'Rayong',
                    'ราชบุรี': 'Ratchaburi',
                    'ลพบุรี': 'Lop Buri',
                    'ลำปาง': 'Lampang',
                    'ลำพูน': 'Lamphun',
                    'เลย': 'Loei',
                    'ศรีสะเกษ': 'Si Sa Ket',
                    'สกลนคร': 'Sakon Nakhon',
                    'สงขลา': 'Songkhla',
                    'สตูล': 'Satun',
                    'สมุทรปราการ': 'Samut Prakan',
                    'สมุทรสงคราม': 'Samut Songkhram',
                    'สมุทรสาคร': 'Samut Sakhon',
                    'สระแก้ว': 'Sa Kaeo',
                    'สระบุรี': 'Saraburi',
                    'สิงห์บุรี': 'Sing Buri',
                    'สุโขทัย': 'Sukhothai',
                    'สุพรรณบุรี': 'Suphan Buri',
                    'สุราษฎร์ธานี': 'Surat Thani',
                    'สุรินทร์': 'Surin',
                    'หนองคาย': 'Nong Khai',
                    'หนองบัวลำภู': 'Nong Bua Lam Phu',
                    'อ่างทอง': 'Ang Thong',
                    'อำนาจเจริญ': 'Amnat Charoen',
                    'อุดรธานี': 'Udon Thani',
                    'อุตรดิตถ์': 'Uttaradit',
                    'อุทัยธานี': 'Uthai Thani',
                    'อุบลราชธานี': 'Ubon Ratchathani'
                    

                }
                state_eng_name = province_mapping.get(raw_state, raw_state)
                
                state_name = data.get('จังหวัด', '').replace('จังหวัด', '').strip()
                state = self.env['res.country.state'].search([
                    '|', ('name', 'ilike', raw_state), ('name', 'ilike', state_eng_name),
                    ('country_id.code', '=', 'TH')
                ], limit=1)

                self.write({
                    'name': data.get('ชื่อนิติบุคคล'),
                    'vat': clean_vat,
                    'street': data.get('ที่ตั้งสำนักงานใหญ่'),
                    'street2': f"ต.{data.get('ตำบล')} อ.{data.get('อำเภอ')}",
                    'city': data.get('อำเภอ'),
                    'zip': data.get('รหัสไปรษณีย์'),
                    'state_id': state.id if state else False,
                    'country_id': self.env.ref('base.th').id,
                    'objective': data.get('วัตถุประสงค์'),
                    'registration_date': data.get('วันที่จดทะเบียน'),
                    'business_type_name': data.get('ประเภทธุรกิจ')
                })
            else:
                raise UserError(_("API Error (%s): %s") % (response.status_code, response.text))
        except Exception as e:
            raise UserError(_("การเชื่อมต่อล้มเหลว: %s") % str(e))