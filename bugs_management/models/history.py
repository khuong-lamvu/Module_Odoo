from odoo import api, fields, models

class History(models.Model):
    _name = 'bugs_management.history'
    _description = 'Lịch sử'
    _order = 'create_date DESC'

    bug_id = fields.Many2one('bugs_management.bugs', string='Lỗi', required=True, ondelete='cascade')
    ngay_xu_ly = fields.Date(string='Ngày xử lý', default=fields.Date.today())
    nguoi_xu_ly = fields.Many2one(related='bug_id.employee_id', string='Người xử lý', readonly=True, track_visibility='always')

    trang_thai_moi = fields.Selection([
        ('choxuly', 'Chờ xử lý'),
        ('dangxuly', 'Đang xử lý'),
        ('hoanthanh', 'Hoàn thành'),
        ('huy', 'Hủy')
    ], string='Trạng thái', track_visibility='onchange')

    mo_ta_qua_trinh = fields.Text(string='Mô tả quá trình xử lý lỗi')
    # Thêm trường cờ "archive"
    archive = fields.Boolean(string='Đã lưu trữ', default=False)

    # Thêm hàm lưu thông tin
    def save_history(self):
        self.ensure_one()
        if self.bug_id.trang_thai != self.trang_thai_moi:
            self.bug_id.write({
                'trang_thai': self.trang_thai_moi,
            })

    def unlink(self):
        # Xóa các bản ghi liên quan trước khi xóa bản ghi chính
        self.mapped('bug_id').unlink()
        # Đánh dấu bản ghi là đã lưu trữ thay vì xóa
        self.write({'archive': True})
        return True