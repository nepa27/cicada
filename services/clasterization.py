from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances


def get_clasters(embeddings: list) -> list:
    # Вычисляем матрицу попарных косинусных расстояний
    # Косинусное расстояние = 1 - косинусное сходство
    distances = cosine_distances(embeddings)

    # Применяем агломеративную кластеризацию с порогом расстояния
    # Порог определяем экспериментально: чем меньше, тем более похожи тексты должны быть, чтобы попасть в один кластер.
    # Начнем с 0.3 (это значит, что косинусное расстояние между текстами в кластере не больше 0.3 → сходство > 0.7)
    clustering = AgglomerativeClustering(
        n_clusters=None,  # не фиксируем число кластеров
        distance_threshold=0.3,  # порог расстояния (главный параметр!)
        metric='precomputed',  # используем готовую матрицу расстояний
        linkage='average'  # средняя связь между кластерами
    )

    # Обучаем модель на матрице расстояний
    clustering.fit(distances)

    labels = clustering.labels_
    return labels
