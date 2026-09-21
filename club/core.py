from .models import *
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from .models import UserFavorite, EventClassInformation, StudentClubData
import json

# display_type:   是否显示类型
# types:          所有的类型

# id:        EventClassInformation 的主键
# name:      课程名字
# cnum:      当前已经报名的人数
# rnum:      当前还剩下的名额数
# desc:      简介
# full_desc: 是否有完整简介
# type:      课程类型对应的 id
# status:
#  0 表示可以选且用户报的课程数未达上限
#  1 表示可以选但用户报的课程数已达上限
#  2 表示这门课程禁止报名
#  3 表示这门课程已满
#  4 表示用户已报名这个课程且可以取消
#  5 表示用户已报名这个课程但不能取消
#  6 表示为 0 状态但选课还未开始
#  7 表示为 4 状态但选课还未开始


def fit_constraints(x, A):

    for (t1, c1, t2, c2, C) in A:
        if x[t1]*c1+x[t2]*c2 > C:
            return False

    return True


def get_selection_data(selection_object, user, is_started, ignore_forbid=False):
    res = {}
    # Materialise the type set once so we don't hit the DB multiple times.
    type_list = list(EventClassType.objects.filter(event_id=selection_object))
    # Pull the related class_type together with each class to avoid a query per row.
    class_set = EventClassInformation.objects.filter(
        event_id=selection_object).select_related('class_type')
    cstt_set = EventClassTypeConstraints.objects.filter(
        event_id=selection_object)
    # Use the *_id attributes so we don't trigger a query per constraint row.
    cstt_list = [(i.type_id1_id, i.coef_1, i.type_id2_id, i.coef_2, i.C)
                 for i in cstt_set]
    user_num = {}

    for i in type_list:
        user_num[i.pk] = 0

    if len(type_list) <= 1:
        res['display_type'] = False
    else:
        res['display_type'] = True
        res['types'] = {i.pk: i.type_name for i in type_list}

    res['data'] = []

    favorite_ids = set(
        UserFavorite.objects.filter(user=user).values_list("event_class_id", flat=True)
    )

    # Enrolled count per class for the whole event in a single grouped query.
    enrolled_counts = dict(
        StudentSelectionInformation.objects
        .filter(info_id__event_id=selection_object)
        .values('info_id')
        .annotate(cnt=Count('id'))
        .values_list('info_id', 'cnt')
    )

    # This user's selections for the whole event in a single query.
    user_selection_locked = dict(
        StudentSelectionInformation.objects
        .filter(info_id__event_id=selection_object, user_id=user)
        .values_list('info_id', 'locked')
    )

    for c in class_set:

        c_type = c.class_type

        c_res = {}
        c_res['type'] = c_type.pk
        c_res['full_desc'] = c.hf_desc
        c_res['link'] = c.full_desc
        c_res['id'] = c.pk
        c_res['desc'] = c.desc
        c_res['name'] = c.name
        c_res['mnum'] = c.max_num
        c_res['cnum'] = enrolled_counts.get(c.pk, 0)
        c_res['rnum'] = max(c.max_num - c_res['cnum'], 0)

        c_res['is_favorite'] = (c.pk in favorite_ids)

        if c.pk not in user_selection_locked:

            if (c.forbid_chs and (not ignore_forbid)):
                c_res['status'] = 2

            elif c_res['rnum'] == 0:
                c_res['status'] = 3

            else:
                c_res['status'] = 0

        else:
            user_num[c_type.pk] += 1

            if user_selection_locked[c.pk]:
                c_res['status'] = 5

            else:
                c_res['status'] = 4

        res['data'].append(c_res)

    # res['data'] = sorted(res['data'], key=lambda x: (x['type'], x['name']))
    
    res['data'] = sorted(
        res['data'],
        key=lambda x: (-int(x['is_favorite']), x['type'], x['name'])
    )

    data_count = len(res['data'])

    for c_id in range(data_count):

        if res['data'][c_id]['status'] == 0:

            user_num[res['data'][c_id]['type']] += 1

            if not fit_constraints(user_num, cstt_list):
                res['data'][c_id]['status'] = 1

            user_num[res['data'][c_id]['type']] -= 1

        if (not is_started) and (res['data'][c_id]['status'] == 0):
            res['data'][c_id]['status'] = 6

        if (not is_started) and (res['data'][c_id]['status'] == 4):
            res['data'][c_id]['status'] = 7

    return res


def convert_selection_data_to_html(data):

    row_content = '''
    <tr>
        <td class='op-content'>
            %s
        </td>
        <td class='status-content'>
            %s
        </td>
        <td class='name-content'>
            %s
        </td>
        <td>
            <div class='desc-full'>
                <div class='col'>
                    <div class='inner'>
                        %s
                    </div>
                </div>
                %s
            </div>
        </td>
        %s
        <td class='cnum-content'>
            %s
        </td>
        <td class='rnum-content'>
            %s
        </td>
        <td class='op-content'>
            %s
        </td>
    </tr>
    '''

    result = ''
    dtype = data['display_type']

    # disa = False

    # for c in data['data']:
    #     if c['status']==4 or c['status']==5:
    #         disa = True
    #         break

    for c in data['data']:
        name = c['name']
        logo = ''

        if c['status'] == 4 or c['status'] == 5 or c['status'] == 7:
            logo = "<span><i class='fa-solid fa-check fa-lg'></i></span>"

        elif c['status'] == 2:
            logo = "<span><i class='fa-solid fa-ban fa-lg'></i></span>"

        elif c['status'] == 3:
            logo = "<span style='margin-left:0.15rem;'><i class='fa-solid fa-xmark fa-xl'></i></span>"

        desc = c['desc']

        # type_div = ''
        type_div = "<td class='type-content'></td>"

        if dtype:
            type_div = "<td class='type-content'>%s</td>" % (
                data['types'][c['type']])

        cnum = str(c['cnum'])
        rnum = str(c['rnum'])

        class_id = str(c['id'])

        if c['status'] == 0:
            op_content = "<button class='btn btn-primary sign-up' id='%s'>报名</button>" % (
                class_id)

        elif c['status'] == 1:
            op_content = "<button class='btn btn-primary' id='%s' disabled>不可报名</button>" % (
                class_id)

        elif c['status'] == 2:
            op_content = "<button class='btn btn-danger' id='%s' disabled>不可报名</button>" % (
                class_id)

        elif c['status'] == 3:
            op_content = "<button class='btn btn-primary' id='%s' disabled>已满</button>" % (
                class_id)

        elif c['status'] == 4:
            op_content = "<button class='btn btn-danger cancel-sign-up' id='%s'>取消报名</button>" % (
                class_id)

        elif c['status'] == 5:
            op_content = "<button class='btn btn-danger' id='%s' disabled>不可取消</button>" % (
                class_id)

        # elif disa:
        #     op_content = "<button class='btn border-success' id='%s' disabled>已选其他</button>" % (class_id)

        elif c['status'] == 6:
            op_content = "<button class='btn btn-primary' id='%s' disabled>未开始</button>" % (
                class_id)

        else:
            op_content = "<button class='btn btn-danger id='%s' disabled>未开始</button>" % (
                class_id)

        full_desc_button = ''
        
        if c['full_desc']:
            full_desc_button = "<a href='%s' target='_blank'>详情</a>" % (c['link'])

        if c['is_favorite'] == 1:
            favorite_content = "<button class='btn favorite-btn-cancel cancel-favorite' id='%s'>取消收藏</button>" % (
                class_id)
        
        else:
            favorite_content = "<button class='btn favorite-btn add-favorite' id='%s'>收藏</button>" % (
                class_id)

        result += row_content % (favorite_content, logo, name, desc,
                                 full_desc_button, type_div, cnum, rnum, op_content)

    return result


def get_selection_list(rec):

    # Fetch the related user and prefetch their groups so the loop below does
    # not issue a query per student (and per student's group set).
    sel_list = StudentSelectionInformation.objects.filter(
        info_id=rec).select_related('user_id').prefetch_related('user_id__groups')

    res = {'locked': [], 'other': []}

    for s in sel_list:
        cur_data = {'n': s.user_id.student_real_name, 'e': s.user_id.email,
                    'g': ','.join([g.name for g in s.user_id.groups.all()])}
        if s.locked:
            res['locked'].append(cur_data)
        res['other'].append(cur_data)

    return res
