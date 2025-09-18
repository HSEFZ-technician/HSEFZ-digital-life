from django.http import JsonResponse, HttpRequest
import mysql.connector
from django.conf import settings
import club_main.settings
import re

def verify_student(request: HttpRequest):
    student_id = request.GET.get('id', None)

    if not student_id:
        return JsonResponse({'error': '缺少 "id" 参数'}, status=400)

    if not re.match(r'^\d{9}$', student_id):
        return JsonResponse({'error': '无效的 "id" 格式，必须是9位数字'}, status=400)

    cnx = None
    cursor = None
    try:
        cnx = mysql.connector.connect(**settings.DB_CONFIG)
        cursor = cnx.cursor()

        query = "SELECT student_real_name, email FROM club_studentclubdata WHERE student_id = %s;"
        
        cursor.execute(query, (student_id,))
        
        result = cursor.fetchone()

        if result:
            name, email = result
            data = {
                'name': name,
                'email': email,
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'error': '未找到该学生'}, status=404)

    except mysql.connector.Error as err:
        return JsonResponse({'error': f'数据库错误: {err}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'服务器内部错误: {str(e)}'}, status=500)
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

