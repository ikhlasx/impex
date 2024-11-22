from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, current_app
from flask_login import login_required, current_user
from app.models import Shop, ButtonPress
from app import db
from sqlalchemy import func
import pandas as pd
from io import BytesIO
from datetime import datetime
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


admin = Blueprint('admin', __name__, url_prefix='/admin')



def get_formatted_stats():
    try:
        # Get statistics
        stats_query = db.session.query(
            Shop.shop_name,
            ButtonPress.button_number,
            func.count(ButtonPress.id).label('play_count')
        ).join(
            ButtonPress, Shop.id == ButtonPress.shop_id, isouter=True
        ).group_by(
            Shop.shop_name,
            ButtonPress.button_number
        ).all()

        # Format statistics
        stats_dict = {}
        video_names = {
            1: '55 inch UHD',
            2: '55 Inch Mini LED',
            3: '65 Inch Gaming QLED',
            4: '65 Inch Mini LED'
        }

        # Initialize all shops with zero counts
        shops = Shop.query.all()
        for shop in shops:
            stats_dict[shop.shop_name] = {
                '55 inch UHD': 0,
                '55 Inch Mini LED': 0,
                '65 Inch Gaming QLED': 0,
                '65 Inch Mini LED': 0
            }

        # Fill in actual counts
        for shop_name, button_number, count in stats_query:
            if button_number in video_names:
                stats_dict[shop_name][video_names[button_number]] = count

        return stats_dict
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {str(e)}")
        return {}


@admin.route('/')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.player'))

    stats_dict = get_formatted_stats()
    shops = Shop.query.filter(Shop.shop_name != 'admin').all()

    return render_template('admin.html',
                           stats=stats_dict,
                           shops=shops,
                           datetime=datetime)


@admin.route('/register', methods=['POST'])
@login_required
def register():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.player'))

    shop_name = request.form.get('shop_name')
    password = request.form.get('password')

    if not shop_name or not password:
        flash('Shop name and password are required.', 'error')
        return redirect(url_for('admin.dashboard'))

    if Shop.query.filter_by(shop_name=shop_name).first():
        flash('Shop name already exists.', 'error')
        return redirect(url_for('admin.dashboard'))

    try:
        new_shop = Shop(shop_name=shop_name)
        new_shop.set_password(password)
        db.session.add(new_shop)
        db.session.commit()
        flash(f'Shop "{shop_name}" registered successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error registering shop: {str(e)}")
        flash('An error occurred while registering the shop.', 'error')

    return redirect(url_for('admin.dashboard'))


@admin.route('/delete/<int:shop_id>', methods=['POST'])
@login_required
def delete(shop_id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.player'))

    shop = Shop.query.get_or_404(shop_id)
    if shop.shop_name == 'admin':
        flash('Cannot delete admin account.', 'error')
        return redirect(url_for('admin.dashboard'))

    try:
        ButtonPress.query.filter_by(shop_id=shop.id).delete()
        db.session.delete(shop)
        db.session.commit()
        flash(f'Shop "{shop.shop_name}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting shop: {str(e)}")
        flash('An error occurred while deleting the shop.', 'error')

    return redirect(url_for('admin.dashboard'))


@admin.route('/download')
@login_required
def download():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.player'))

    try:
        stats_dict = get_formatted_stats()

        # Create DataFrame
        df = pd.DataFrame.from_dict(stats_dict, orient='index')

        # Create Excel file in memory
        output = BytesIO()

        # Create Excel writer
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Write the data
            df.to_excel(writer, sheet_name='Video Statistics', index=True)

            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Video Statistics']

            # Define styles
            header_font = Font(bold=True, size=12)
            header_fill = PatternFill(start_color='E2EFD9', end_color='E2EFD9', fill_type='solid')
            centered = Alignment(horizontal='center')
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )

            # Style the headers (including index header)
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = centered
                cell.border = border

            # Add title
            worksheet.insert_rows(1, 2)  # Insert 2 rows at the top
            title_cell = worksheet.cell(row=1, column=1, value='Video Player Statistics')
            title_cell.font = Font(bold=True, size=14)
            title_cell.alignment = centered

            # Add timestamp
            timestamp_cell = worksheet.cell(row=2, column=1,
                                            value=f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            timestamp_cell.font = Font(italic=True)

            # Merge cells for title and timestamp
            worksheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(df.columns) + 1)
            worksheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(df.columns) + 1)

            # Auto-adjust column widths
            for idx, column in enumerate(df.columns, 1):
                column_letter = get_column_letter(idx + 1)  # +1 because index column is first
                max_length = max(
                    len(str(column)),
                    df[column].astype(str).apply(len).max()
                )
                adjusted_width = max_length + 2
                worksheet.column_dimensions[column_letter].width = adjusted_width

            # Adjust index column width
            worksheet.column_dimensions['A'].width = max(
                len(str(idx)) for idx in df.index
            ) + 5

            # Add borders and center alignment to all cells
            for row in worksheet.iter_rows(min_row=3):  # Start from data rows
                for cell in row:
                    cell.border = border
                    cell.alignment = Alignment(horizontal='center', vertical='center')

        # Reset file pointer
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'video_statistics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )

    except Exception as e:
        current_app.logger.error(f"Error exporting Excel: {str(e)}")
        flash('Error exporting data to Excel.', 'error')
        return redirect(url_for('admin.dashboard'))