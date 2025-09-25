from django.http import JsonResponse, HttpRequest
from django.db import connection
import re

def verify_student(request: HttpRequest):
    mail = request.GET.get('mail', None)

    if not mail:
        return JsonResponse({'error': '缺少 "mail" 参数'}, status=400)

    # if not re.match(r'^\d{9}$', mail):
    #     return JsonResponse({'error': '无效的 "mail" 格式，必须是9位数字'}, status=400)

    try:
        with connection.cursor() as cursor:
            
            query = "SELECT student_real_name, student_id FROM club_studentclubdata WHERE username=\"%s\";"
            
            cursor.execute(query%mail)
            
            result = cursor.fetchone()

            if result:
                name, id = result
                data = {
                    'name': name,
                    'id': id,
                }
                return JsonResponse(data, status=200)
            else:
                return JsonResponse({'error': '未找到该学生'}, status=404)

    except Exception as e:
        return JsonResponse({'error': f'服务器内部错误: {str(e)}'}, status=500)