# Interactive-Cylindrical-Stitcher
Interactive image stitching program using SIFT, Cylindrical Projection, and Alpha Blending in OpenCV.

Cylindrical Projection과 실시간으로 조리개 값을 변환하는 GUI를 통해 왜곡을 최소화한 파노라마 생성을 목표로 합니다.

---

## 주요 기능 및 기술 요약 (Key Features)


* **SIFT(Scale-Invariant Feature Transform)**: 조명이나 크기 변화가 심한 실외 환경에서도 강인하게 특징점을 추출합니다.
* **Lowe's Ratio Test**: KNN 매칭(K=2) 후 가장 가까운 두 매칭점의 거리 비율을 검사하여 신뢰도가 낮은 Outlier를 효과적으로 제거합니다.
* **RANSAC 기반 Homography 추정**: 매칭점 중 유효한 데이터만을 선별하여 기하학적 오차를 최소화한 최적의 변환 행렬($H$)을 도출합니다.

### Cylindrical Projection
* Planar View 시 가장자리 이미지가 무한히 늘어나는 현상을 해결하기 위해 원통형 좌표계 투영을 추가 기능으로 구현하였습니다.
* 아래 수식을 코드로 직접 구현하여 평면 이미지를 가상의 원통면으로 Warping 
  $$x_{cyl} = f \cdot \arctan\left(\frac{x - x_c}{f}\right) + x_c$$
  $$y_{cyl} = f \cdot \frac{y - y_c}{\sqrt{(x - x_c)^2 + f^2}} + y_c$$

###  실시간 파라미터 튜닝 GUI 
* **Interactive Trackbar**: OpenCV `createTrackbar`를 활용하여 사용자가 실시간으로 초점 거리($f$)를 조절하며 정합 결과의 수평과 왜곡을 미세 조정할 수 있습니다.
* **Dynamic Feedback**: 트랙바 조작 시마다 투영 및 정합 루프가 재실행되어 최적의 파노라마 지점을 즉각적으로 찾을 수 있습니다.

### Seamless Blending
* **Alpha Blending**: 겹치는 부위의 급격한 노출 차이와 경계선을 완화하기 위해 addWeighted를 이용한 5:5 가중치 합성을 적용하여 자연스러운 연결을 구현했습니다.
---

## 프로세스

### Preprocessing
* 고해상도 원본 사진(3024x4032)의 연산 부담을 줄이고 매칭 신뢰도를 높이기 위해 가로 600px로 Resize를 수행합니다.

### Recursive Homography
* 첫 번째 이미지(`st1.jpg`)를 월드 좌표계의 기준으로 설정합니다.
* 이후 각 이미지 쌍($i, i-1$)에 대해 계산된 호모그래피 행렬($H_{step}$)을 전역 행렬($H_{total}$)에 누적 곱셈하여 모든 사진을 하나의 캔버스 좌표계로 통합합니다.
  $$H_{total} = H_{total} \times H_{step}$$

### 3. 후처리 및 최적화
* **Automatic Cropping**: 정합 후 발생하는 캔버스의 거대한 검은색 여백을 boundingRect를 통해 자동으로 인식하여 유효한 영상 영역만 정밀하게 잘라냅니다.
* **Display Scaling**: 결과물이 모니터 해상도를 초과할 경우를 대비하여, 화면 출력 시에는 가로 1000px로 최적화하여 보여주고 저장은 원본 품질 그대로 수행합니다.

---



< 왼쪽의 Controlpanel에서 트랙바 조절을 통해 $f$값 조절 >
<img width="1678" height="826" alt="스크린샷 2026-04-28 211850" src="https://github.com/user-attachments/assets/ed66ea07-cf26-430e-9172-1c803b31481a" />




<img width="1613" height="962" alt="스크린샷 2026-04-28 211933" src="https://github.com/user-attachments/assets/a5116864-3e8f-4bc7-b787-4f20fa48dd4e" />



< $f$값 약 600일 때 최적 >
<img width="2097" height="1156" alt="final" src="https://github.com/user-attachments/assets/2e07e04b-5d38-4df0-a88c-2c0ab9ce3db2" />





### 실행 방법
```bash
python image_stitching.py
