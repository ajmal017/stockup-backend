import com.szkingdom.kcbpcli.KCBPClient;
import com.szkingdom.kcbpcli.KCBPClient1;
import com.szkingdom.kcbpcli.KCBPClientC;
import com.szkingdom.kcbpcli.KCBPInt;
import com.szkingdom.kcbpcli.KCBPReturnCode;
import com.szkingdom.kcbpcli.tagKCBPConnectOption;


public class Test {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		//create connection
		int ret = -1;
		long handle = -1;
		String address = "192.168.88.3";	
		KCBPClient1 pKCBPCli = new KCBPClient1();
		
		KCBPInt Handle = new KCBPInt();
		   
		if((ret = pKCBPCli.KCBPCLI_Init(Handle))==1) {
			System.out.println("Init kcbp failed.");
			return;
		}
		
		handle = Handle.x;
		
		System.out.println("======= Handle.x="+handle);
		
		//建立连接
		pKCBPCli.KCBPCLI_SetOption(handle, KCBPClientC.KCBP_OPTION_CRYPT,
				new Integer(0));
		pKCBPCli.KCBPCLI_SetOption(handle,
				KCBPClientC.KCBP_OPTION_COMPRESS, new Integer(0));

		tagKCBPConnectOption stKCBPConnection = new tagKCBPConnectOption();
		stKCBPConnection.szServerName = "KCBP01";// "KCBP01";//"KCBP01";//"kcbp1";
		stKCBPConnection.nProtocal = 0;
		stKCBPConnection.szAddress = address;
		stKCBPConnection.nPort = 21000;
		stKCBPConnection.szSendQName = "req1";
		stKCBPConnection.szReceiveQName = "ans1";
		
		if (pKCBPCli.KCBPCLI_SetOption(handle,
				KCBPClientC.KCBP_OPTION_CURRENT_CONNECT, stKCBPConnection) != 0) {
			System.out.println("set connect option error!");
			return;
		}

		System.out.println("1");

		if (pKCBPCli.KCBPCLI_SetOption(handle,
				KCBPClientC.KCBP_OPTION_AUTHENTICATION, new Integer(0)) != 0) {
			System.out.println("set connect option error!");
			return;
		}
				System.out.println("2");

//		if (pKCBPCli.KCBPCLI_SetIntOption(handle,
//				KCBPClientC.KCBP_OPTION_TRACE, 1) != 0) {
//			System.out.println("set connect option error!");
//			return;
//		}
			
		ret = pKCBPCli.KCBPCLI_SQLConnect(handle, "KCBP01", "KCXP00", "888888");
		if (ret != 0) {
			System.out.println("KCBPCLI_SQLConnect failed, ret = " + ret + ", server:"+address);
			pKCBPCli.KCBPCLI_Exit(handle);
			return;
		}
		System.out.println("3");

		pKCBPCli.KCBPCLI_SetCliTimeOut(handle, 200);
		//pKCBPCli.KCBPCLI_SetSystemParam(handle, 7, "tradedb");

		//发请求
		//String funcCode = "410203";		//登录柜台
//		String funcCode = "410510";		//查资金
		String funcCode = "1101010";		//
		pKCBPCli.KCBPCLI_BeginWrite(handle);
		pKCBPCli.KCBPCLI_SetValue(handle, "funcid", "1101010");
		pKCBPCli.KCBPCLI_SetValue(handle, "custid", "");
		pKCBPCli.KCBPCLI_SetValue(handle, "custorgid", "");
		pKCBPCli.KCBPCLI_SetValue(handle, "trdpwd", "");
		pKCBPCli.KCBPCLI_SetValue(handle, "netaddr", "");
		pKCBPCli.KCBPCLI_SetValue(handle, "orgid", "");
		pKCBPCli.KCBPCLI_SetValue(handle, "operway", "");
		pKCBPCli.KCBPCLI_SetValue(handle, "ext", "");
		pKCBPCli.KCBPCLI_SetValue(handle, "version", "20090917");

//		ret = pKCBPCli.KCBPCLI_SQLExecute(handle, funcCode);
		ret = pKCBPCli.KCBPCLI_CallProgramAndCommit(handle, funcCode);
		if (ret != KCBPReturnCode.RC_OK) {
			System.out.println("KCBPCLI_CallProgramAndCommit error, error code : " + ret);
			System.out.println("err msg: "+pKCBPCli.KCBPCLI_GetErrorMsg(handle) + ",ip=" + address);
			if (ret == 2054 || ret == 2055 || ret == 2003) {
				//重新建立连接
			}
			return;
		}
//		String pp = pKCBPCli.KCBPCLI_GetValue(handle,"msg",100);
//		System.out.println("msg="+pp);

		//读取结果集
		//第一个结果集包含功能调用成功与否的信息
		pKCBPCli.KCBPCLI_RsOpen(handle);
		//String tableName = pKCBPCli.KCBPCLI_SQLGetCursorName(handle, 100);
		//int ColNum = pKCBPCli.KCBPCLI_SQLNumResultCols(handle);
		//String colNames1 = pKCBPCli.KCBPCLI_RsGetColNames(handle, 500);
		if (pKCBPCli.KCBPCLI_SQLFetch(handle) == 0) {
			int bpReturnCode = Integer.parseInt(pKCBPCli.KCBPCLI_RsGetCol(
					handle, 2));
			if (bpReturnCode != KCBPReturnCode.RC_OK) {
				System.out.println("功能调用失败,错误信息: " + pKCBPCli.KCBPCLI_RsGetCol(handle, 3));
				return;
			}
		} else {
			System.out.println("KCBPCLI_SQLFetch error");
			return;
		}
		System.out.println("5");

		//第二个结果集是返回的结果数据,是个二维表
		ret = pKCBPCli.KCBPCLI_SQLMoreResults(handle);
		if(ret!=0){
			System.out.println("KCBPCLI_SQLMoreResults error : " + ret);
			return;
		}
		//ColNum = pKCBPCli.KCBPCLI_SQLNumResultCols(handle);// 此句为什么不能代替RsGetColNum??
		//int RowNum = pKCBPCli.KCBPCLI_RsGetRowNum(handle);
//		tableName = pKCBPCli.KCBPCLI_RsGetCursorName(handle, 100);
		String[] colNames = pKCBPCli.KCBPCLI_RsGetColNames(handle, 500).split(
				",");
		for (int i = 0; i < colNames.length; i++){
			System.out.print( colNames[i].trim() );
			System.out.print("\t");
		}
		System.out.println("\n-----------------------------------------------------------------------------");

		int count = 0;
//		while (pKCBPCli.KCBPCLI_RsFetchRow(handle) == 0) {	//kcbpcp和刘闽的Client_test都是用的KCBPCLI_SQLFetch，对于某些BP报文，pKCBPCli.KCBPCLI_RsFetchRow读不出来，但KCBPCLI_SQLFetch能读出来
		while (pKCBPCli.KCBPCLI_SQLFetch(handle) == 0) {
			if((count++)<600){
				for (int i = 0; i < colNames.length; i++) {
					System.out.print(pKCBPCli.KCBPCLI_RsGetCol(handle, i + 1).trim());
					System.out.print("\t");
				}
				System.out.println();
			}
		}

		//结束读取结果集
		pKCBPCli.KCBPCLI_SQLCloseCursor(handle);
		
		//断开连接
		pKCBPCli.KCBPCLI_DisConnectForce(handle);
		pKCBPCli.KCBPCLI_Exit(handle);
	}

}
