from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Criteria(models.Model):
    _name = 'manage_reviews.criteria'
    _description = 'Tiêu chí đánh giá'

    name = fields.Char(string='Tên tiêu chí', required=True)  # Phải sử dụng biến là "name" nó mới chạy bình thường

    trong_so_tc = fields.Integer(string='Trọng số (1 - 4)')

    #Mô tả các mưc độ tiêu chí
    mucdo_yeu = fields.Char(string='Yếu (1)')
    mucdo_trungbinh = fields.Char(string='Trung Bình (2)')
    mucdo_kha = fields.Char(string='Khá (3)')
    mucdo_tot = fields.Char(string='Tốt (4)')

    # Add a section - Add a note
    sequence = fields.Integer()
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")],
        default=False, help="Technical field for UX purpose.")

    #Tạo liên kết đến biểu mẫu
    form_id = fields.Many2one('manage_reviews.template', string='Biểu mẫu')

    # Xử lý ngoại lệ - Trọng số trong khoảng từ 1 đến 4
    @api.constrains('trong_so_tc')
    def _check_trong_so_tc(self):
        for record in self:
            if record.trong_so_tc and (record.trong_so_tc < 1 or record.trong_so_tc > 4):
                raise ValidationError(_('Trọng số phải nằm trong khoảng từ 1 đến 4!'))