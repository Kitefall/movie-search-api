import asyncio
import logging

import joblib
from config import ModelSettings, RabbitmqSettings
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitMessage, RabbitQueue
from log import get_logger
from msg_schema import HistoryPredictMessage

settings = RabbitmqSettings()
model_settings = ModelSettings()

logger = get_logger(logger_name=__name__, level=logging.INFO)

broker = RabbitBroker(url=settings.RABBITMQ_URL)
app = FastStream(broker=broker)

tfidf = joblib.load('tfidf_vectorizer.joblib')
knn = joblib.load('knn_model.joblib')

request_queue = RabbitQueue(
    settings.REQUEST_QUEUE,
    durable=True,
    auto_delete=False)

response_queue = RabbitQueue(
    settings.RESPONSE_QUEUE,
    durable=True,
    auto_delete=False)


@broker.subscriber(
        request_queue,
        no_ack=True
)
async def process_model_input(msg: RabbitMessage, data: HistoryPredictMessage):
    try:
        query_text = data.data

        query_vec = tfidf.transform([query_text])
        distances, indices = knn.kneighbors(
            query_vec,
            n_neighbors=model_settings.COUNT_FILMS
        )

        data.result = str(indices[0].tolist())
        data.status = 'True'

    except Exception as ex:
        logger.error(
            "Ошибка %s",
            str(ex)
        )
        data.result = None
        data.status = 'False'

    await broker.publish(
        data,
        queue=response_queue
    )
    await msg.ack()


async def main():
    await app.run()

if __name__ == '__main__':
    asyncio.run(main())
