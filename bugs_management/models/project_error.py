from odoo import api, fields, models
from datetime import date
import datetime
from datetime import datetime
from odoo.exceptions import ValidationError


class ProjectError(models.Model):
    _name = 'bugs_management.project_error'
    _description = 'Dự án lỗi'
    _rec_name = 'ten_du_an'

    checked = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Check'),
    ],
        default='0')

    ma_du_an = fields.Char(string='Mã dự án lỗi', required=True)
    ten_du_an = fields.Char(string='Tên dự án lỗi', required=True)
    # Thêm trường One2many để liên kết với các bản ghi của model "Lỗi"
    loi_ids = fields.One2many('bugs_management.bugs', 'project_error_id', string='Các lỗi của dự án')

    quan_ly_du_an = fields.Many2one('hr.employee', string='Quản lý dự án')

    # Trường One2many liên kết với model "bugs_management.chuc_nang_du_an"
    chuc_nang_ids = fields.One2many('bugs_management.function_project', 'project_error_id', string='Chức năng dự án')

    # Trường tính để tính tổng số lượng lỗi của dự án
    sum_error = fields.Integer(string='Tổng số lỗi', compute='_compute_sum_error', store=True)
    # Add a computed field to count the number of times the issues have been handled
    so_lan_xu_ly_loi = fields.Integer(string='Số lần xử lý lỗi', compute='_compute_so_lan_xu_ly_loi')

    @api.depends('loi_ids.history_ids')
    def _compute_so_lan_xu_ly_loi(self):
        for project_error in self:
            project_error.so_lan_xu_ly_loi = len(project_error.loi_ids.mapped('history_ids'))

    @api.depends('loi_ids.trang_thai')
    def _compute_sum_error(self):
        for project_error in self:
            project_error.sum_error = len(
                project_error.loi_ids.filtered(lambda x: x.trang_thai in ['choxuly', 'dangxuly']))

    # Phương thức tính tổng số lỗi (dùng để cập nhật lại giá trị khi có thay đổi trong các lỗi)
    def update_sum_error(self):
        for project_error in self:
            project_error.sum_error = len(
                project_error.loi_ids.filtered(lambda x: x.trang_thai in ['choxuly', 'dangxuly']))

    def action_issue(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Issues',
            'res_model': 'bugs_management.bugs',
            'domain': [('project_error_id', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
    #Lấy danh sách dự án
    @api.model
    def get_select_project_error(self):
        project_errors = self.search([])
        project_errors_result = []
        for project_error in project_errors:
            project_errors_result.append({
                'id': project_error.id,
                'name': project_error.ten_du_an,
            })
        return project_errors_result
    #Lấy tổng danh sách dự án lỗi
    @api.model
    def get_project_error_bug_count(self, project_error_id, from_date, to_date):
        # Chuyển đổi định dạng của ngày trước khi sử dụng trong domain
        from_date = datetime.strptime(from_date, '%d/%m/%Y').date()
        to_date = datetime.strptime(to_date, '%d/%m/%Y').date()

        # Kiểm tra project_error_id có giá trị None hay không
        if project_error_id is None:
            print("project_error_id không được phép để trống.")
            return 0  # Hoặc giá trị phù hợp để xử lý trong trường hợp lỗi
        # Chuyển đổi project_error_id thành kiểu int (nếu thỏa mãn điều kiện chuyển đổi)
        try:
            project_error_id = int(project_error_id)
        except ValueError:
            # Xử lý lỗi khi không thể chuyển đổi project_error_id thành kiểu int
            print("Không thể chuyển đổi project_error_id thành kiểu int.")
            return 0  # Hoặc giá trị phù hợp để xử lý trong trường hợp lỗi

        domain = [
            ('project_error_id', '=', project_error_id),
            ('ngay_tao_loi', '>=', from_date),
            ('ngay_tao_loi', '<=', to_date),
        ]
        # print(from_date)
        # print(to_date)
        # print(type(from_date))
        # print(type(to_date))
        # print(type(project_error_id))
        bug_count = self.env['bugs_management.bugs'].search_count(domain)
        # test = self.env['bugs_management.bugs'].search([])
        # print(bug_count)
        return bug_count
    #Lấy danh sách dự án đã hoàn thành
    @api.model
    def get_completed_errors_count(self, project_error_id, from_date, to_date):
        # Chuyển đổi định dạng của ngày trước khi sử dụng trong domain
        from_date = datetime.strptime(from_date, '%d/%m/%Y').date()
        to_date = datetime.strptime(to_date, '%d/%m/%Y').date()

        # Kiểm tra project_error_id có giá trị None hay không
        if project_error_id is None:
            print("project_error_id không được phép để trống.")
            return 0  # Hoặc giá trị phù hợp để xử lý trong trường hợp lỗi
        # Chuyển đổi project_error_id thành kiểu int (nếu thỏa mãn điều kiện chuyển đổi)
        try:
            project_error_id = int(project_error_id)
        except ValueError:
            # Xử lý lỗi khi không thể chuyển đổi project_error_id thành kiểu int
            print("Không thể chuyển đổi project_error_id thành kiểu int.")
            return 0  # Hoặc giá trị phù hợp để xử lý trong trường hợp lỗi

        domain = [
            ('project_error_id', '=', project_error_id),
            ('ngay_tao_loi', '>=', from_date),
            ('ngay_tao_loi', '<=', to_date),
            ('trang_thai', '=', 'hoanthanh'),
        ]
        completed_error_count = self.env['bugs_management.bugs'].search_count(domain)
        # print(completed_error_count)
        return completed_error_count
    # Lấy danh sách dự án chưa hoàn thành
    @api.model
    def get_incomplete_errors_count(self, project_error_id, from_date, to_date):
        # Chuyển đổi định dạng của ngày trước khi sử dụng trong domain
        from_date = datetime.strptime(from_date, '%d/%m/%Y').date()
        to_date = datetime.strptime(to_date, '%d/%m/%Y').date()
        # Kiểm tra project_error_id có giá trị None hay không
        if project_error_id is None:
            print("project_error_id không được phép để trống.")
            return 0  # Hoặc giá trị phù hợp để xử lý trong trường hợp lỗi
        # Chuyển đổi project_error_id thành kiểu int (nếu thỏa mãn điều kiện chuyển đổi)
        try:
            project_error_id = int(project_error_id)
        except ValueError:
            # Xử lý lỗi khi không thể chuyển đổi project_error_id thành kiểu int
            print("Không thể chuyển đổi project_error_id thành kiểu int.")
            return 0  # Hoặc giá trị phù hợp để xử lý trong trường hợp lỗi
        domain = [
            ('project_error_id', '=', project_error_id),
            ('ngay_tao_loi', '>=', from_date),
            ('ngay_tao_loi', '<=', to_date),
            ('trang_thai', 'in', ['choxuly', 'dangxuly']),  # Lọc lỗi có trạng thái chờ xử lý hoặc đang xử lý
        ]
        incomplete_error_count = self.env['bugs_management.bugs'].search_count(domain)
        # print(incomplete_error_count)
        return incomplete_error_count
    # Lấy danh sách dự án đã hủy
    @api.model
    def get_cancel_errors_count(self, project_error_id, from_date, to_date):
        # Chuyển đổi định dạng của ngày trước khi sử dụng trong domain
        from_date = datetime.strptime(from_date, '%d/%m/%Y').date()
        to_date = datetime.strptime(to_date, '%d/%m/%Y').date()
        # Kiểm tra project_error_id có giá trị None hay không
        if project_error_id is None:
            print("project_error_id không được phép để trống.")
            return 0  # Hoặc giá trị phù hợp để xử lý trong trường hợp lỗi
        # Chuyển đổi project_error_id thành kiểu int (nếu thỏa mãn điều kiện chuyển đổi)
        try:
            project_error_id = int(project_error_id)
        except ValueError:
            # Xử lý lỗi khi không thể chuyển đổi project_error_id thành kiểu int
            print("Không thể chuyển đổi project_error_id thành kiểu int.")
            return 0  # Hoặc giá trị phù hợp để xử lý trong trường hợp lỗi
        domain = [
            ('project_error_id', '=', project_error_id),
            ('ngay_tao_loi', '>=', from_date),
            ('ngay_tao_loi', '<=', to_date),
            ('trang_thai', '=', 'huy'),
        ]
        cancel_error_count = self.env['bugs_management.bugs'].search_count(domain)
        # print(cancel_error_count)
        return cancel_error_count
    # Lấy/thống kê danh sách nhân viên phụ trách xử lý lỗi
    @api.model
    def get_employee_bug_count(self, project_error_id, from_date, to_date):
        # Chuyển đổi định dạng ngày trước khi sử dụng trong domain
        from_date = datetime.strptime(from_date, '%d/%m/%Y').date()
        to_date = datetime.strptime(to_date, '%d/%m/%Y').date()
        # Kiểm tra project_error_id có giá trị None hay không
        if not project_error_id:
            print("project_error_id không được để trống.")
            return []
        try:
            project_error_id = int(project_error_id)
        except ValueError:
            print("Không thể chuyển đổi project_error_id thành kiểu int.")
            return []
        domain = [
            ('project_error_id', '=', project_error_id),
            ('ngay_tao_loi', '>=', from_date),
            ('ngay_tao_loi', '<=', to_date),
        ]

        # Tìm các bản ghi lỗi thỏa điều kiện domain
        bugs = self.env['bugs_management.bugs'].search(domain)

        # Tạo từ điển lưu số lỗi của từng nhân viên phụ trách
        employee_bug_count = {}
        for bug in bugs:
            employee_name = bug.employee_id.name
            employee_bug_count[employee_name] = employee_bug_count.get(employee_name, 0) + 1

        # Tạo danh sách kết quả
        result = [{'employee_name': name, 'bug_count': count} for name, count in employee_bug_count.items()]

        return result
    #  Lấy/thống kê danh sách lỗi theo chức năng
    @api.model
    def get_functionality_bug_count(self, project_error_id, from_date, to_date):
        # Chuyển đổi định dạng ngày trước khi sử dụng trong domain
        from_date = datetime.strptime(from_date, '%d/%m/%Y').date()
        to_date = datetime.strptime(to_date, '%d/%m/%Y').date()
        functionality_bug_count = []

        if not project_error_id:
            print("project_error_id không được để trống.")
            return functionality_bug_count

        try:
            project_error_id = int(project_error_id)
        except ValueError:
            print("Không thể chuyển đổi project_error_id thành kiểu int.")
            return functionality_bug_count

        # Lấy danh sách các chức năng dự án thuộc dự án được chọn
        functionality_records = self.env['bugs_management.function_project'].search(
            [('project_error_id', '=', project_error_id)])

        for functionality in functionality_records:
            # Lọc các lỗi thuộc chức năng và có ngày tạo trong khoảng từ from_date đến to_date
            bug_domain = [('function_project_id', '=', functionality.id),
                          ('ngay_tao_loi', '>=', from_date),
                          ('ngay_tao_loi', '<=', to_date)]
            bug_count = self.env['bugs_management.bugs'].search_count(bug_domain)

            functionality_bug_count.append({
                'functionality_name': functionality.chuc_nang,
                'bug_count': bug_count,
            })
        print(functionality_bug_count)
        return functionality_bug_count
    # Lấy/thống kê thông tin lỗi
    @api.model
    def get_error_data(self, project_error_id, from_date, to_date):
        # Chuyển đổi định dạng ngày trước khi sử dụng trong domain
        from_date = datetime.strptime(from_date, '%d/%m/%Y').date()
        to_date = datetime.strptime(to_date, '%d/%m/%Y').date()

        # Kiểm tra project_error_id có giá trị None hay không
        if not project_error_id:
            print("project_error_id không được để trống.")
            return []

        try:
            project_error_id = int(project_error_id)
        except ValueError:
            print("Không thể chuyển đổi project_error_id thành kiểu int.")
            return []

        domain = [
            ('project_error_id', '=', project_error_id),
            ('ngay_tao_loi', '>=', from_date),
            ('ngay_tao_loi', '<=', to_date),
        ]

        # Tìm các bản ghi lỗi thỏa điều kiện domain
        bugs = self.env['bugs_management.bugs'].search(domain)

        # Tạo danh sách kết quả
        error_data = []
        for bug in bugs:
            error_data.append({
                'name': bug.ten_loi,
                'functionality': bug.function_project_id.chuc_nang,
                'date_created': bug.ngay_tao_loi,
                'status': bug.trang_thai,
            })
        print(error_data)
        return error_data