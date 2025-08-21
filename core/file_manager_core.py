#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理核心模块
功能：管理测试数据文件的创建和保存
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import zipfile
from datetime import datetime

class FileManagerCore:
    """文件管理核心类"""
    
    def __init__(self):
        pass
    
    def save_test_files(self, test_data: List[str], output_dir: str, 
                       file_prefix: str = "test", create_zip: bool = True, 
                       delete_temp_files: bool = False) -> Dict[str, Any]:
        """保存测试文件
        
        Args:
            test_data: 测试数据列表
            output_dir: 输出目录
            file_prefix: 文件前缀
            create_zip: 是否创建zip文件
            delete_temp_files: 是否在创建zip后删除临时文件
            
        Returns:
            保存结果信息
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        
        # 创建.in文件
        for i, data in enumerate(test_data, 1):
            filename = f"{file_prefix}{i:02d}.in"
            file_path = output_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
                if not data.endswith('\n'):
                    f.write('\n')
            
            created_files.append(str(file_path))
        
        result = {
            'output_dir': str(output_path),
            'created_files': created_files,
            'file_count': len(created_files)
        }
        
        # 创建zip文件
        if create_zip:
            zip_path = self.create_zip_file(created_files, output_path, file_prefix)
            result['zip_file'] = zip_path
            
            # 如果需要，删除临时文件
            if delete_temp_files:
                deleted_files = []
                for file_path in created_files:
                    try:
                        Path(file_path).unlink()
                        deleted_files.append(file_path)
                    except Exception:
                        pass
                result['deleted_temp_files'] = deleted_files
        
        return result
    
    def create_zip_file(self, file_paths: List[str], output_dir: Path, 
                       prefix: str = "test") -> str:
        """创建zip文件
        
        Args:
            file_paths: 要打包的文件路径列表
            output_dir: 输出目录
            prefix: 文件前缀
            
        Returns:
            zip文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"{prefix}_data_{timestamp}.zip"
        zip_path = output_dir / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_paths:
                file_path_obj = Path(file_path)
                # 只保存文件名，不保存完整路径
                zipf.write(file_path, file_path_obj.name)
        
        return str(zip_path)
    
    def save_with_solutions(self, test_data: List[str], solutions: List[str], 
                          output_dir: str, file_prefix: str = "test", 
                          delete_temp_files: bool = False) -> Dict[str, Any]:
        """保存测试数据和解答
        
        Args:
            test_data: 测试数据列表
            solutions: 解答列表
            output_dir: 输出目录
            file_prefix: 文件前缀
            delete_temp_files: 是否在创建zip后删除临时文件
            
        Returns:
            保存结果信息
        """
        if len(test_data) != len(solutions):
            raise ValueError("测试数据和解答数量不匹配")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        
        # 创建.in和.out文件
        for i, (data, solution) in enumerate(zip(test_data, solutions), 1):
            # 输入文件
            in_filename = f"{file_prefix}{i:02d}.in"
            in_file_path = output_path / in_filename
            
            with open(in_file_path, 'w', encoding='utf-8') as f:
                f.write(data)
                if not data.endswith('\n'):
                    f.write('\n')
            
            created_files.append(str(in_file_path))
            
            # 输出文件
            out_filename = f"{file_prefix}{i:02d}.out"
            out_file_path = output_path / out_filename
            
            with open(out_file_path, 'w', encoding='utf-8') as f:
                f.write(solution)
                if not solution.endswith('\n'):
                    f.write('\n')
            
            created_files.append(str(out_file_path))
        
        # 创建zip文件
        zip_path = self.create_zip_file(created_files, output_path, file_prefix)
        
        result = {
            'output_dir': str(output_path),
            'created_files': created_files,
            'file_count': len(created_files),
            'zip_file': zip_path
        }
        
        # 如果需要，删除临时文件
        if delete_temp_files:
            deleted_files = []
            for file_path in created_files:
                try:
                    Path(file_path).unlink()
                    deleted_files.append(file_path)
                except Exception:
                    pass
            result['deleted_temp_files'] = deleted_files
        
        return result
    
    def load_template(self, template_path: str) -> Optional[List[Dict[str, Any]]]:
        """加载模板配置
        
        Args:
            template_path: 模板文件路径
            
        Returns:
            模板配置列表，如果加载失败返回None
        """
        try:
            import json
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            return template_data.get('variables', [])
        except Exception:
            return None
    
    def save_template(self, configs: List[Dict[str, Any]], template_path: str, 
                     template_name: str = "自定义模板") -> bool:
        """保存模板配置
        
        Args:
            configs: 变量配置列表
            template_path: 模板文件路径
            template_name: 模板名称
            
        Returns:
            是否保存成功
        """
        try:
            import json
            
            template_data = {
                'name': template_name,
                'created_time': datetime.now().isoformat(),
                'variables': configs
            }
            
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典，如果文件不存在返回None
        """
        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                return None
            
            stat = path_obj.stat()
            
            return {
                'name': path_obj.name,
                'size': stat.st_size,
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'is_file': path_obj.is_file(),
                'is_dir': path_obj.is_dir()
            }
        except Exception:
            return None
    
    def clean_output_dir(self, output_dir: str, file_pattern: str = "test*.in") -> int:
        """清理输出目录
        
        Args:
            output_dir: 输出目录
            file_pattern: 文件匹配模式
            
        Returns:
            删除的文件数量
        """
        try:
            output_path = Path(output_dir)
            if not output_path.exists():
                return 0
            
            deleted_count = 0
            for file_path in output_path.glob(file_pattern):
                if file_path.is_file():
                    file_path.unlink()
                    deleted_count += 1
            
            # 同时删除对应的.out文件
            if file_pattern == "test*.in":
                for file_path in output_path.glob("test*.out"):
                    if file_path.is_file():
                        file_path.unlink()
                        deleted_count += 1
            
            return deleted_count
        except Exception:
            return 0
    
    def validate_output_dir(self, output_dir: str) -> Dict[str, Any]:
        """验证输出目录
        
        Args:
            output_dir: 输出目录路径
            
        Returns:
            验证结果
        """
        result = {
            'valid': False,
            'exists': False,
            'writable': False,
            'message': ''
        }
        
        try:
            output_path = Path(output_dir)
            
            # 检查目录是否存在
            if output_path.exists():
                result['exists'] = True
                if not output_path.is_dir():
                    result['message'] = '路径存在但不是目录'
                    return result
            else:
                # 尝试创建目录
                try:
                    output_path.mkdir(parents=True, exist_ok=True)
                    result['exists'] = True
                except Exception as e:
                    result['message'] = f'无法创建目录: {str(e)}'
                    return result
            
            # 检查是否可写
            test_file = output_path / '.write_test'
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                test_file.unlink()
                result['writable'] = True
                result['valid'] = True
                result['message'] = '目录有效'
            except Exception as e:
                result['message'] = f'目录不可写: {str(e)}'
            
        except Exception as e:
            result['message'] = f'验证目录时出错: {str(e)}'
        
        return result