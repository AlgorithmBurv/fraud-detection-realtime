<!-- 1. Hentikan Semua Container -->

docker stop $(docker ps -aq)

<!-- 2. Hapus Semua Container -->

docker rm $(docker ps -aq)

<!-- 3. Hapus Semua Volume -->

docker volume rm $(docker volume ls -q)

# Docker Cheat Sheet

## **1. Manajemen Container**

| **Perintah**                                       | **Deskripsi**                                       |
| -------------------------------------------------- | --------------------------------------------------- |
| `docker ps`                                        | Menampilkan container yang sedang berjalan          |
| `docker ps -a`                                     | Menampilkan semua container, termasuk yang berhenti |
| `docker run [OPTIONS] IMAGE [COMMAND] [ARG...]`    | Menjalankan container baru                          |
| `docker exec -it <container_id_or_name> /bin/bash` | Masuk ke dalam container (interaktif)               |
| `docker stop <container_id_or_name>`               | Menghentikan container                              |
| `docker start <container_id_or_name>`              | Memulai kembali container yang berhenti             |
| `docker rm <container_id_or_name>`                 | Menghapus container                                 |
| `docker container prune`                           | Menghapus semua container yang berhenti             |
| `docker logs <container_id_or_name>`               | Menampilkan log dari container                      |

## **2. Manajemen Image**

| **Perintah**                                        | **Deskripsi**                        |
| --------------------------------------------------- | ------------------------------------ |
| `docker images`                                     | Menampilkan daftar image yang ada    |
| `docker pull <image_name>`                          | Menarik image dari Docker Hub        |
| `docker build -t <image_name> <path_to_dockerfile>` | Membangun image dari Dockerfile      |
| `docker rmi <image_name_or_id>`                     | Menghapus image                      |
| `docker image prune`                                | Menghapus image yang tidak digunakan |

## **3. Manajemen Volume**

| **Perintah**                         | **Deskripsi**                               |
| ------------------------------------ | ------------------------------------------- |
| `docker volume ls`                   | Menampilkan daftar volume                   |
| `docker volume create <volume_name>` | Membuat volume baru                         |
| `docker volume rm <volume_name>`     | Menghapus volume                            |
| `docker volume prune`                | Menghapus semua volume yang tidak digunakan |

## **4. Manajemen Network**

| **Perintah**                                                   | **Deskripsi**                      |
| -------------------------------------------------------------- | ---------------------------------- |
| `docker network ls`                                            | Menampilkan daftar network         |
| `docker network create <network_name>`                         | Membuat network baru               |
| `docker network connect <network_name> <container_id_or_name>` | Menghubungkan container ke network |
| `docker network rm <network_name>`                             | Menghapus network                  |

## **5. Docker Compose**

| **Perintah**           | **Deskripsi**                                              |
| ---------------------- | ---------------------------------------------------------- |
| `docker-compose up`    | Menjalankan aplikasi multi-container dengan Docker Compose |
| `docker-compose up -d` | Menjalankan Docker Compose di background (detached mode)   |
| `docker-compose ps`    | Menampilkan status container dalam Docker Compose          |
| `docker-compose down`  | Menghentikan container dengan Docker Compose               |
| `docker-compose build` | Membangun ulang container dengan Docker Compose            |

## **6. Informasi dan Diagnostik**

| **Perintah**                            | **Deskripsi**                                             |
| --------------------------------------- | --------------------------------------------------------- |
| `docker info`                           | Menampilkan informasi tentang Docker                      |
| `docker system df`                      | Menampilkan penggunaan ruang disk oleh Docker             |
| `docker stats`                          | Menampilkan statistik penggunaan CPU dan memori container |
| `docker inspect <container_id_or_name>` | Menampilkan informasi rinci tentang container             |

## **7. Perintah Lainnya**

| **Perintah**                   | **Deskripsi**                                                     |
| ------------------------------ | ----------------------------------------------------------------- |
| `docker --version`             | Menampilkan versi Docker                                          |
| `docker search <image_name>`   | Mencari image di Docker Hub                                       |
| `docker stop $(docker ps -aq)` | Menghentikan semua container yang sedang berjalan                 |
| `docker rm $(docker ps -aq)`   | Menghapus semua container                                         |
| `docker container prune`       | Menghapus semua container yang berhenti                           |
| `docker image prune`           | Menghapus semua image yang tidak digunakan                        |
| `docker system prune`          | Menghapus semua container, volume, dan image yang tidak digunakan |
