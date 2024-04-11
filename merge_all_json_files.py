import os
import json


def replace_fran(string):
    fr_en = [['é', 'e'], ['ê', 'e'], ['è', 'e'], ['ë', 'e'], ['à', 'a'], ['â', 'a'], ['ç', 'c'], ['î', 'i'], ['ï', 'i'],
             ['ô', 'o'], ['ù', 'u'], ['û', 'u'], ['ü', 'u'], ['ÿ', 'y']
             ]
    for i in fr_en:
        string = string.replace(i[0], i[1])
    return string


def merge_json_files(directory, output_file):
    try:
        # 清空输出文件
        with open(output_file, 'w', encoding= 'utf-8') as f:
            f.write('')

        # 获取所有后缀为.json的文件
        json_files = [f for f in os.listdir(directory) if f.endswith('.json')]

        # 打印要合并的文件总数
        print(f'要合并的文件总数：{len(json_files)}')

        # 遍历每个JSON文件，合并到输出文件中
        for json_file in json_files:
            print(f'开始合并文件：{json_file}')

            # 读取JSON文件内容
            with open(os.path.join(directory, json_file), 'r', encoding='utf-8') as f:
                json_data = replace_fran(f.read())
                # json_data = f.read()

            # 写入到输出文件中
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(json_data)
                f.write('\n')  # 每个文件之间换行

            # 打印合并完的文件名称和当前all.txt的文件总数
            with open(output_file, 'r',encoding='utf-8') as f:
                current_count = len(f.readlines())

            print(f'合并完成：{json_file}，当前all.txt的文件总数：{current_count}')

        # 打印合并完的文件名称和总的数量
        print('\n合并完成的文件：')
        print('| 文件名称 | 总数量 |')
        print('| -------- | ------ |')
        print(f'| {json_file} | {current_count} |')

    except Exception as e:
        print(f'发生异常：{e}')


if __name__ == '__main__':
    # 使用示例
    directory = 'book'
    output_file = 'all.txt'
    merge_json_files(directory, output_file)
