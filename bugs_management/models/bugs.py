from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Bugs(models.Model):
    _name = 'bugs_management.bugs'
    _description = 'Lỗi dự án'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = 'ten_loi'

    ten_loi = fields.Char(string='Tên lỗi', required=True)
    muc_do_loi = fields.Selection([
        ('thap', 'Thấp'),
        ('trungbinh', 'Trung bình'),
        ('uutien', 'Ưu tiên')
    ], string='Mức độ lỗi', default='', required=True)
    trang_thai = fields.Selection([
        ('choxuly', 'Chờ xử lý'),
        ('dangxuly', 'Đang xử lý'),
        ('hoanthanh', 'Hoàn thành'),
        ('huy', 'Hủy'),
    ], string='Trạng thái', default='choxuly', track_visibility='onchange')

    mo_ta_loi = fields.Html(string='Mô tả', required=True)
    ngay_tao_loi = fields.Date(string='Ngày tạo lỗi', default=fields.Date.today())

    # Tạo liên kết đến module project và employee
    # project_id = fields.Many2one('project.project', string='Dự án', required=True)
    # project_name = fields.Char(string='Tên dự án', related='project_id.name', store=True)

    #Tạo liên kết đến model project_error - Trường Many2one để liên kết với model "Dự Án Lối"
    project_error_id = fields.Many2one('bugs_management.project_error', string='Dự án lỗi')
    project_error_name = fields.Char(string='Dự án lỗi', related='project_error_id.ten_du_an', store=True)
    # Tạo liên kết đến module employee
    employee_id = fields.Many2one('hr.employee', string='Người phụ trách')
    employee_name = fields.Char(string='Người phụ trách', related='employee_id.name', store=True)
    # Tạo liên kết đến model history
    history_ids = fields.One2many('bugs_management.history', 'bug_id', string='Lịch sử báo cáo')

    # Tạo liên kết đến model function_project - Trường Many2many để liên kết với model "Chức năng Dự Án"
    function_project_id = fields.Many2one('bugs_management.function_project', string='Chức năng dự án')

    # Thêm hàm xử lý cho nút Button xử lý - wizard
    def action_process_bug(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Báo cáo công việc xử lý lỗi',
            'res_model': 'bugs_management.history',
            'view_mode': 'form',
            'view_id': self.env.ref('bugs_management.bugs_management_history_form_view').id,
            'target': 'new',
            'context': {'default_bug_id': self.id, 'default_trang_thai_moi': self.trang_thai},
        }
