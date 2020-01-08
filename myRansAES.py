import glob
import os, random, struct
import sys
from Cryptodome.Cipher import AES


def encrypt(key, in_filename, chunksize=64 * 1024):
    '''
    :param key: 암호화 키 16 or 24 or 32바이트
    :param in_filename: 암호화 할 파일 이름
    :param out_filename: 암호화 된 파일 이름
    :param chunksize: 파일에서 읽을 바이트 수 -> 16의 배수여야 함. AES blocksize 16바이트
    :return:
    '''
    out_filename = in_filename+'.jonghyun'  # 출력이름 설정
    iv = os.urandom(16)  # 16Byte 값 랜덤 생성, 복호화 할 때 필요 함
    encryptor = AES.new(key, AES.MODE_CBC, iv)  # AES를 이용해서 CBC 모드 암호화 키를 생성
    filesize = os.path.getsize(in_filename)  # 입력 파일의 크기

    with open(in_filename, 'rb') as infile:  # 입력 파일을 바이너리 읽기 모드로 열기
        with open(out_filename, 'wb') as outfile:  # 출력 파일을 바이너리 쓰기 모드로 열기
            outfile.write(struct.pack('<Q', filesize))  # 파일크기를 바이트로 패킹하여 출력파일에 쓰기 Q :unsigned long long
            outfile.write(iv)  # 랜덤생성한 16Byte 쓰기
            while True:
                chunk = infile.read(chunksize)  # chunksize 만큼 파일 읽기
                if len(chunk) == 0:  # 읽은 값의 길이가 0이면 반복 중지
                    break
                elif len(chunk) % 16 != 0:  # 읽은 값의 길이가 16의 배수가 아닐때
                    chunk += b' ' * (16 - len(chunk) % 16)  # 부족한 곳을 채워 16의 배수로 만들어주기
                outfile.write(encryptor.encrypt(chunk))  # AES로 암호화 하여 출력 파일에 쓰기


def decrypt(key, in_filename, chunksize=24 * 1024):
    out_filename = os.path.splitext(in_filename)[0]  # 입력파일의 확장자를 추출
    with open(in_filename, 'rb') as infile:  # 입력 파일을 바이너리 읽기 모드로 열기
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]  # 언패킹하여 파일크기 구하기
        iv = infile.read(16)  # 16byte 읽기
        decryptor = AES.new(key, AES.MODE_CBC, iv)  # AES는 대칭키를 사용하기때문에 encryptor와 같음
        with open(out_filename, 'wb') as outfile:  # 출력 파일을 바이너리 쓰기 모드로 열기
            while True:
                chunk = infile.read(chunksize)  # chunksize만큼 읽기
                if len(chunk) == 0:  # 읽은 값의 길이가 0이면 반복 중지
                    break
                outfile.write(decryptor.decrypt(chunk))  # 읽은 값을 복호화해서 출력 파일에 쓰기
            outfile.truncate(origsize)  # 출력 파일에서 원본 파일의 크기만큼 자르기


key = b'hello world!!!!!'  # AES 암호화에사용될 키값을 바이너리로 생성
startPath = os.getcwd() + '\\test\\**'  # 경로 설정
# 암호화
for filename in glob.iglob(startPath, recursive=True):  # 설정한 경로에서 탐색
    if (os.path.isfile(filename)):  # 파일이 존재할 때
        print('Encrypting> ' + filename)  # 암호화 한 파일명 출력
        encrypt(key, filename)  # 암호화
        os.remove(filename)  # 기존파일 제거

# 복호화
for filename in glob.iglob(startPath, recursive=True):  # 설정한 경로에서 탐색
    if (os.path.isfile(filename)):  # 파일이 존재할 때
        fname, ext = os.path.splitext(filename)  # 파일명과 확장자 추출
        if (ext == '.jonghyun'):  # 내가 암호화한 파일인 경우
            print('Decrypting> ' + filename)  # 복호화 한 파일명 출력
            decrypt(key, filename)  # 복호화
            os.remove(filename)  # 암호화 된 기존 파일 제거