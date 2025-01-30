from django.contrib.auth.models import User
from parents.models import Parent
from students.models import Student

def create_parent_with_children(parent_name, phone_number, children_ids):
    # 创建 User
    username = f"{parent_name}_{phone_number}"
    password = phone_number[-6:]  # 默认密码为手机号后6位
    user = User.objects.create_user(username=username, password=password)
    
    # 创建 Parent
    parent = Parent.objects.create(
        user=user,
        parent_name=parent_name,
        phone_number=phone_number
    )

    # 关联孩子
    children = Student.objects.filter(id__in=children_ids)  # 通过 ID 查找学生
    parent.children.set(children)

    # 更新孩子的 parent_names 字段
    for child in children:
        # 如果已有保護者名，则追加新家长名字
        if child.parent_names:
            current_names = child.parent_names.split(', ')
            if parent_name not in current_names:
                current_names.append(parent_name)
                child.parent_names = ', '.join(current_names)
        else:
            # 如果没有保護者名，则直接添加
            child.parent_names = parent_name
        child.save()

    print(f"Parent {parent_name} created and associated with children: {[child.student_name for child in children]}")
    return parent


