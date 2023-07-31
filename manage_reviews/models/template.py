from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date
import datetime

class Template(models.Model):
    _name = 'manage_reviews.template'
    _description = 'Biểu mẫu'

    name = fields.Char(string='Tên biểu mẫu', required=True)
    ngay_tao = fields.Date(string='Ngày tạo', required=True)

    criteria_ids = fields.One2many('manage_reviews.criteria', 'form_id', string='Tiêu chí')