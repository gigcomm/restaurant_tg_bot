import pandas as pd
from sqlalchemy import *
from src.config import *
import tracemalloc
from reportlab.pdfgen import canvas
tracemalloc.start()
output_directory = "C:\\Users\\Игорь\\Desktop\\coursework_bot\\output_db\\output.pdf"

output_file = "output.pdf"

async def export_to_pdf(output_director):
    async with async_session() as session:
        result = await session.scalars(select(Orders))
        session.close()

        df_combined = pd.DataFrame(
            [(orders.id, orders.order_adress, orders.order_date, orders.price, orders.status_id)
             for orders in result],
            columns=['ID', 'Adress', 'Date order', 'Price', 'ID status']
        )
        c = canvas.Canvas(output_director)
        c.setFont("Helvetica", 14)
        # Начальные координаты для вывода текста
        x = 100
        y = 750

        for _, row in df_combined.iterrows():
            text = ', '.join(map(str, row.tolist()))
            c.drawString(x, y, text)
            # Уменьшаем y для вывода следующей строки ниже
            y -= 20

        c.save()

