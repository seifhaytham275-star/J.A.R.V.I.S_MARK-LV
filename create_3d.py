import trimesh

# 1. إنشاء أشكال 3D أساسية بالكود
# إنشاء مكعب
box = trimesh.creation.box(extents=[2, 2, 2])

# إنشاء كرة
sphere = trimesh.creation.sphere(radius=1.3)

# 2. عمل عمليات هندسية (Boolean Operations)
# مثال: قطع الكرة من المكعب (Boolean Difference)
# الناتج هيكون مكعب مفرغ منه شكل كروي!
final_shape = box.difference(sphere)

# 3. تلوين المجسم
final_shape.visual.face_colors = [100, 200, 255, 255] # لون أزرق فاتح

# 4. عرض المجسم فوراً في نافذة تفاعلية (تقدر تلفه بالماوس وتعمل Zoom)
print("🚀 جاري عرض المجسم الـ 3D...")
final_shape.show()

# 5. حفظ المجسم بصيغة OBJ أو STL لو حابب تفتحه على بلندر أو تطبعه 3D
final_shape.export("my_model.obj")
print("✅ تم حفظ المجسم باسم my_model.obj")