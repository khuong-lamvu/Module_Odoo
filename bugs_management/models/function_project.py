from odoo import api, fields, models

class FunctionProject(models.Model):
    _name = 'bugs_management.function_project'
    _description = 'Chức năng dự án'
    _rec_name = 'chuc_nang'

    chuc_nang = fields.Char(string='Chức năng')
    project_error_id = fields.Many2one('bugs_management.project_error', string='Dự án lỗi')
    # Thêm trường One2many để liên kết với các bản ghi của model "Lỗi" có cùng chức năng
    loi_ids = fields.One2many('bugs_management.bugs', 'function_project_id', string='Các lỗi của dự án')

    # Thêm trường tính số lượng lỗi
    so_luong_loi = fields.Integer(string='Số lỗi', compute='_compute_so_luong_loi')
    @api.depends('loi_ids', 'loi_ids.trang_thai')
    def _compute_so_luong_loi(self):
        for function in self:
            function.so_luong_loi = len(function.loi_ids.filtered(lambda loi: loi.trang_thai in ['choxuly', 'dangxuly']))

