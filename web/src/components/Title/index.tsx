import { ArrowLeftOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
const Title = (props: any) => {
  const navigate = useNavigate();
  return (
    <div className="title">
      <div className="flex ailgn-center" style={{marginBottom: 12 }}>
        {props.back && (
          <span onClick={() => navigate(-1)} style={{width: 24,height:24,display:'flex',justifyContent:"center",alignItems:'center',marginRight:5,background:'rgb(135, 138, 171)', cursor: "pointer"}}>
            <ArrowLeftOutlined style={{color:'white'}}/>
          </span>
        )}
        <h2 style={{ color: "#26244c"}}>{props.title}</h2>
      </div>
      <p style={{ color: "#878aab", marginBottom: 12,fontSize:14 }}>{props.subtitle}</p>
    </div>
  );
};

export default Title;
